import logging
import os
import stat

from textwrap import dedent
from typing import Any

logger = logging.getLogger(__name__)


class DockerfileWriter:
    """This class formats Dockerfiles to be used in the docker-compose.yml file."""

    @staticmethod
    def write_dockerfile(path: str, content: str) -> None:
        # Normalize line endings
        content: str = content.replace("\r\n", "\n").replace("\r", "\n")

        try:
            # Write file
            with open(path, "w", newline="\n") as f:
                f.write(dedent(content))

            # Make dockerfile executable (chmod +x)
            st: Any = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

            logger.info(f"✅ Dockerfile written and made executable: {path}")

        except Exception as e:
            logger.error(f"❌ Failed to write Dockerfile to {path}: {str(e)}")
            raise
