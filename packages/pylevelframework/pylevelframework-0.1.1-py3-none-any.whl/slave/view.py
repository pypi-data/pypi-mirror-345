import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from fleetvue import FleetVue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('view.log')  # File handler
    ]
)

logger = logging.getLogger('slave.view')

class View:
    """View class for handling template rendering using FleetVue"""
    
    _view_paths: List[str] = []
    _shared_data: Dict[str, Any] = {}
    _fleetvue = FleetVue()
    
    @classmethod
    def add_path(cls, path: str):
        """Add a view path to search for templates"""
        logger.info(f"Adding view path: {path}")
        cls._view_paths.append(path)
        
    @classmethod
    def share(cls, key: str, value: Any):
        """Share data across all views"""
        logger.info(f"Sharing data: {key}")
        cls._shared_data[key] = value
        
    @classmethod
    def _format_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data before passing to template"""
        formatted_data = {}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                formatted_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, list):
                formatted_data[key] = [cls._format_data(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                formatted_data[key] = cls._format_data(value)
            else:
                formatted_data[key] = value
                
        return formatted_data
        
    @classmethod
    def make(cls, view_name: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Render a view template with the given data using FleetVue"""
        logger.info(f"Rendering view: {view_name}")
        view_path = cls._get_view_path(view_name)
        logger.info(f"View path: {view_path}")
        
        # Format data before merging
        formatted_data = cls._format_data(data or {})
        formatted_shared = cls._format_data(cls._shared_data)
        merged_data = {**formatted_shared, **formatted_data}
        
        logger.debug(f"Formatted data: {formatted_data}")
        logger.debug(f"Formatted shared data: {formatted_shared}")
        logger.info(f"Merged data keys: {list(merged_data.keys())}")
        
        try:
            # Read template file
            with open(view_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            logger.debug(f"Template content length: {len(template_content)}")
            
            # Process with FleetVue
            result = cls._fleetvue.render(template_content, merged_data)
            logger.info("Rendering successful")
            return result
        except Exception as e:
            logger.error(f"Error rendering view {view_name}: {str(e)}", exc_info=True)
            return f"<!-- Error rendering view: {str(e)} -->"
        
    @classmethod
    def _get_view_path(cls, view_name: str) -> str:
        """Get the full path to a view file"""
        view_path = view_name.replace('.', '/')
        view_path = f"{view_path}.html"
        
        for base_path in cls._view_paths:
            full_path = os.path.join(base_path, view_path)
            logger.debug(f"Checking path: {full_path}")
            if os.path.exists(full_path):
                return full_path
                
        raise FileNotFoundError(f"View [{view_name}] not found.")
        
    @classmethod
    def exists(cls, view_name: str) -> bool:
        """
        Check if a view exists
        
        Args:
            view_name: The name of the view file (without extension)
            
        Returns:
            bool: True if view exists, False otherwise
        """
        try:
            cls._get_view_path(view_name)
            return True
        except FileNotFoundError:
            logger.warning(f"View not found: {view_name}")
            return False 