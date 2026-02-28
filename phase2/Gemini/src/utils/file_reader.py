from typing import List
from src.models.point import Point

class FileReader:
    """
    Utility class for reading point coordinates from a file.
    """
    
    @staticmethod
    def read_points(file_path: str) -> List[Point]:
        """
        Reads a file containing coordinates and returns a list of Point objects.
        
        Args:
            file_path: Absolute or relative path to the input file.
            
        Returns:
            A list of Point instances representing valid coordinates.
            
        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If a line in the file cannot be parsed into coordinates.
        """
        points = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                
                parts = clean_line.split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid coordinate format at line {line_number}. Expected two numbers separated by a comma.")
                
                try:
                    x = float(parts[0].strip())
                    y = float(parts[1].strip())
                    points.append(Point(x, y))
                except ValueError:
                    raise ValueError(f"Invalid coordinate format at line {line_number}. Expected two numbers separated by a comma.")
                    
        return points
