
import os
from git import Repo
from . import constants_globs as constants
from .logger import setup_logger

logger = setup_logger('pixi')

def clone_repo(repo_url: str, destination: str, branch: str = "main") -> None:
        """
        Clones a Git repository to a specified destination.
    
        Args:
            repo_url (str): The URL of the Git repository.
            destination (str): The local path where the repository will be cloned.
            branch (str, optional): The branch to clone. Defaults to "main".
        """
        try:
            Repo.clone_from(repo_url, destination)
            logger.info(f"Repository cloned successfully to {destination}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

def clone_required() -> None:
    """Clones the required repositories for Pixi
    """
    for repo, val in constants.need_to_clone.items():
        logger.info(f"Cloning {repo} repository from {val['url']} branch {val['branch']} ...")
        if os.path.exists(repo):
            logger.info(f"{repo} already exists, skipping...")
            continue
        clone_repo(val["url"], repo, branch=val["branch"])
