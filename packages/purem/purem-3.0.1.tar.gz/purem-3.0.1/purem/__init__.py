from purem.env_config import load_env_config

from purem.core import Purem


purem = Purem(licenced_key=load_env_config().PUREM_LICENSE_KEY)
