import os
import multiprocessing as mp
import asyncio
from concurrent.futures import ProcessPoolExecutor

from .Extractors.ExtractorStrategy import ExtractorStrategy
from ..Logging import Debug

class Engine():
    """Engine for moving data across plattforms and across on-prem/cloud"""

    def __init__(self):
        """Initialize the DatMover engine. Takes the ExtractStrategy as input (i.e NetezzaExtractor, OracleExtractor etc.)"""
        self.cpu_count = os.cpu_count() or 4
        self.pool = ProcessPoolExecutor(max_workers=8 or (self.cpu_count - 2))

    @staticmethod
    def parallel_process(worker_func: object, args_list: list[tuple], num_workers: int = None):
        '''
        Executes a worker function 'worker_func' in parallel using a number multiple processes defined by the 'num_workers' variable.

        Args:
            worker_func (function): The function that each worker process should execute.
            args_list (list): A list of tuples, where each tuple contains arguments for worker_func.
            num_workers (int, optional): Number of parallel workers. Defaults to max(4, CPU count - 2).

        Returns:
            list: List of results from worker processes if applicable.
        '''

        # Determine the number of CPU cores to use
        if num_workers is None:
            num_workers = max(4, os.cpu_count() - 2) #failsafe slik at noen kjerner er tilgjengelig for systemet

        num_processes = min(num_workers, len(args_list)) # sørger for at ingen prosesser får mer en angitt num_workers, men spawner bare opptil så mange oppgaver den har dersom num_workers > len(jobber_som_skal_kjøres)

        process_list = []

        # Create and start all worker processes
        for i in range(num_processes):

            process = mp.Process(target=worker_func, args=args_list[i])

            process.daemon = True  # Ensure processes exit when main program exits. This ensures no orphans or zombies
            process_list.append(process)
            process.start()

        return process_list  # Return the list of running processes   
    
    
    @staticmethod
    def determine_file_offsets(file_name: str, num_chunks: int):
        """Determine file offsets for parallel reading based on line breaks."""
        file_size = os.path.getsize(file_name)
        chunk_size = max(1, file_size // num_chunks)

        offsets = [0]
        with open(file_name, 'rb') as f:
            while True:
                next_offset = offsets[-1] + chunk_size
                if next_offset >= file_size:
                    break  # Don’t overshoot the file
                f.seek(next_offset)
                f.readline()  # Move to end of current line
                new_offset = f.tell()
                if new_offset >= file_size or new_offset <= offsets[-1]:
                    break  # EOF or duplicate offset
                offsets.append(new_offset)

        if offsets[-1] < file_size:
            offsets.append(file_size)  # Always include the last chunk

        Debug.log(f"DEBUG: File offsets computed: {offsets}", "INFO")
        return offsets

    
    @staticmethod
    def export_to_file(extractor: ExtractorStrategy, output_path: str, fully_qualified_table_name: str, filter_column: str = None, filter_value: str = None, verbose: bool = False)->tuple:
        """Utilizes the selected Extractor to export database(s) to a csv file."""
        
        header, csv_file = extractor.export_external_table(output_path, fully_qualified_table_name, filter_column, filter_value, verbose)
        return header, csv_file
    
    @staticmethod
    def calculate_chunks(external_table: str, compression: int = 4):
        """Calculates how many chunks to split the file into. Note that this calculation is just an estimate and may not be accurate."""
        
        unzipped_chunk_filesize = 400 * 1024 * 1024 * compression   # 200 MB zipped (added compression_factor in order to account for the compression factor of gzip on table data)
        
        total_filesize = os.path.getsize(external_table)
        
        if total_filesize > unzipped_chunk_filesize:
            num_chunks = int(total_filesize // unzipped_chunk_filesize) + 1 # ensures that at least three chunks is created (trekker fra 1 lenger nede i koden)
        else:
            num_chunks = 1

        Debug.log(f"\nTotal filesize: {total_filesize // (1024*1024)} mb\nnumber of chunks: {num_chunks - 1}\n", 'INFO')
        
        return num_chunks