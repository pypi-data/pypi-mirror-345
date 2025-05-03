import uuid

from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from pathlib import Path

from pydantic import Field, model_validator

from RTN.models import SettingsModel


class VersionProfile(SettingsModel):
    """
    Extended SettingsModel that includes version-specific metadata.
    
    A version profile represents a specific configuration for media content, 
    including settings for media type, content categories, and upgrade policies.
    Each profile is stored as a separate JSON file in the configured directory.
    
    Attributes:
        version_id (str): Unique identifier for this version profile.
        media_type (str): Type of media this profile is for ("movie" or "show").
        anime (bool): Whether this profile is for anime content.
        kids (bool): Whether this profile is for children's content.
        sports (bool): Whether this profile is for sports content.
        dubbed_only (bool): Whether to restrict to dubbed content only.
        symlink_path (str): Path where content should be symlinked.
        enable_upgrades (bool): Whether to enable automatic quality upgrades.
        upgrade_resolution_to (str): Target resolution for upgrades.
    """
    # Version metadata fields
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(default="New Profile")  # Keeping name for UI display purposes
    media_type: Literal["movie", "show"] = Field(default="movie")
    anime: bool = Field(default=False)
    kids: bool = Field(default=False)
    sports: bool = Field(default=False)
    dubbed_only: bool = Field(default=False)
    symlink_path: str = Field(default="")

    # Upgrade settings
    enable_upgrades: bool = Field(default=False)
    upgrade_resolution_to: Literal["2160p", "1080p", "720p"] = Field(default="1080p")
    
    @model_validator(mode="after")
    def validate_profile(self):
        """Validate the profile configuration and set default values."""
        # Set a default symlink path if empty
        if not self.symlink_path:
            # Base folder based on media type
            media_folder = "shows" if self.media_type == "show" else "movies"
            
            # Add prefixes based on content categories
            prefixes = []
            if self.anime:
                prefixes.append("anime")
            if self.kids:
                prefixes.append("kids")
            if self.sports:
                prefixes.append("sports")
            
            # Combine prefixes with media folder
            if prefixes:
                self.symlink_path = f"{'-'.join(prefixes)}-{media_folder}"
            else:
                self.symlink_path = media_folder
                
        return self
    
    def save_to_file(self, directory: Union[str, Path]) -> Path:
        """
        Save this profile to a JSON file in the specified directory.
        
        Args:
            directory: Directory where the profile should be saved
            
        Returns:
            Path: The path to the saved file
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # Create a safe filename from the profile name
        safe_name = self.name.lower().replace(" ", "-")
        file_path = directory / f"{safe_name}.json"
        
        # Save the profile to the file
        self.save(file_path)
        return file_path

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'VersionProfile':
        """
        Load a profile from a JSON file.
        
        Args:
            file_path: Path to the profile JSON file
            
        Returns:
            VersionProfile: The loaded profile
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        return cls.load(file_path)


class VersionHandler:
    """
    Manages multiple version profiles in a configuration directory.
    
    This class provides methods for loading, saving, and managing different
    version profiles stored as JSON files in a specified directory.
    
    Attributes:
        config_directory (Path): Directory where profile JSON files are stored
        active_profile (Optional[VersionProfile]): Currently active profile
        profiles (Dict[str, VersionProfile]): Cache of loaded profiles
    """
    
    def __init__(self, config_directory: Union[str, Path]):
        """
        Initialize the version handler with a configuration directory.
        
        Args:
            config_directory: Directory to store profile JSON files
        """
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(parents=True, exist_ok=True)
        self.active_profile: Optional[VersionProfile] = None
        self.profiles: Dict[str, VersionProfile] = {}
        
    def list_profiles(self) -> List[str]:
        """
        Get a list of available profile names in the config directory.
        
        Returns:
            List[str]: Names of available profiles (without .json extension)
        """
        return [f.stem for f in self.config_directory.glob("*.json")]
    
    def load_profile(self, name: str) -> VersionProfile:
        """
        Load a profile by name.
        
        Args:
            name: Name of the profile to load (without .json extension)
            
        Returns:
            VersionProfile: The loaded profile
            
        Raises:
            FileNotFoundError: If the profile doesn't exist
        """
        file_path = self.config_directory / f"{name}.json"
        
        try:
            profile = VersionProfile.load_from_file(file_path)
            self.profiles[name] = profile
            self.active_profile = profile
            return profile
        except Exception as e:
            raise
    
    def save_profile(self, profile: VersionProfile, name: Optional[str] = None) -> str:
        """
        Save a profile to the config directory.
        
        Args:
            profile: The profile to save
            name: Optional name to save as (default: use profile.name)
            
        Returns:
            str: The name of the saved profile
        """
        if name:
            profile.name = name

        file_path = profile.save_to_file(self.config_directory)
        profile_name = file_path.stem
        self.profiles[profile_name] = profile
        return profile_name

    def create_profile(self, name: str, **kwargs) -> VersionProfile:
        """
        Create a new profile with the given name and settings.
        
        Args:
            name: Name for the new profile
            **kwargs: Settings to apply to the new profile
            
        Returns:
            VersionProfile: The newly created profile
        """
        profile = VersionProfile(name=name, **kwargs)
        self.save_profile(profile)
        self.active_profile = profile
        return profile
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile by name.
        
        Args:
            name: Name of the profile to delete
            
        Returns:
            bool: True if the profile was deleted, False otherwise
        """
        file_path = self.config_directory / f"{name}.json"
        
        if not file_path.exists():
            return False
            
        file_path.unlink()
        if name in self.profiles:
            del self.profiles[name]
            
        if self.active_profile and self.active_profile.name.lower().replace(" ", "-") == name:
            self.active_profile = None
            
        return True
    
    def get_active_profile(self) -> Optional[VersionProfile]:
        """
        Get the currently active profile.
        
        Returns:
            Optional[VersionProfile]: The active profile or None if no profile is active
        """
        return self.active_profile
    
    def check_upgrades(self) -> List[VersionProfile]:
        """
        Check all profiles for upgrade eligibility.
        
        Returns:
            List[VersionProfile]: Profiles eligible for upgrade
        """
        eligible_profiles = []
        now = datetime.now()

        for name in self.list_profiles():
            try:
                profile = self.profiles.get(name) or self.load_profile(name)
                if not profile.enable_upgrades:
                    continue

                hours_since_upgrade = (now - profile.last_upgraded).total_seconds() / 3600
                if hours_since_upgrade >= profile.upgrade_interval:
                    eligible_profiles.append(profile)
            except Exception:
                raise

        return eligible_profiles