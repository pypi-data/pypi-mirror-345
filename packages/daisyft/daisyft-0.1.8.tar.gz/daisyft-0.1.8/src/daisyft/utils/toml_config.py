"""
TOML configuration utilities for DaisyFT projects.
"""
from pathlib import Path
import tomli
import tomli_w
import typer
from typing import Dict, Any, Optional

from .config import ProjectConfig, BinaryMetadata
from .console import console

def load_config(config_path: Optional[Path] = None) -> ProjectConfig:
    if config_path is None:
        config_path = Path(".daisyft") / "daisyft.toml"
        
    if not config_path.exists():
        return ProjectConfig()  # Return default config if file doesn't exist
    
    try:
        with open(config_path, "rb") as f:
            data = tomli.load(f)
        
        project_data = data.get('project', {})
        server_data = data.get('server', {})
        paths_data = data.get('paths', {})
        binary_data = data.get('binary')
        
        paths = {}
        for key, value in paths_data.items():
            paths[key] = Path(value)
            
        if 'app_path' in project_data and isinstance(project_data['app_path'], str):
            project_data['app_path'] = Path(project_data['app_path'])
        
        binary_metadata = None
        if binary_data:
            binary_metadata = BinaryMetadata.from_dict(binary_data)
        
        config = ProjectConfig(
            style=project_data.get('style', ProjectConfig.style),
            theme=project_data.get('theme', ProjectConfig.theme),
            app_path=project_data.get('app_path', ProjectConfig.app_path),
            host=server_data.get('host', ProjectConfig.host),
            port=server_data.get('port', ProjectConfig.port),
            live=server_data.get('live', ProjectConfig.live),
            paths=paths or ProjectConfig.paths,
            binary_metadata=binary_metadata,
        )
        
        # Set previous_style if it exists in the data
        if 'previous_style' in project_data:
            config.previous_style = project_data['previous_style']
        
        return config
        
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {e}")
        return ProjectConfig()  # Return default config on error

def save_config(config: ProjectConfig, config_path: Optional[Path] = None) -> None:
    if config_path is None:
        config_path = Path(".daisyft") / "daisyft.toml"
        
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'project': {
                'style': config.style,
                'theme': config.theme,
                'app_path': str(config.app_path),
            },
            'server': {
                'host': config.host,
                'port': config.port,
                'live': config.live,
            },
            'paths': {
                key: str(value) for key, value in config.paths.items()
            },
        }
        
        if hasattr(config, 'previous_style') and config.previous_style is not None:
            data['project']['previous_style'] = config.previous_style
                
        if config.binary_metadata:
            data['binary'] = config.binary_metadata.to_dict()
                
        with open(config_path, "wb") as f:
            tomli_w.dump(data, f)
            
    except Exception as e:
        console.print(f"[red]Error saving configuration:[/red] {e}")
        raise typer.Exit(1) 