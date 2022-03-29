import configparser
import os

import colorama
from halo import Halo
from requests import Session
from retry_requests import retry
from termcolor import cprint

from ghstats.es_queries import viewer_query

colorama.init()
home_dir = os.path.expanduser("~")
config = configparser.ConfigParser()
spinner = Halo(text='Checking if the token is valid', spinner='dots')
my_session = retry(Session(), retries=2, backoff_factor=10)


def config_dir_path():
  return os.path.join(home_dir, ".ghstats")


def config_file_path():
  return os.path.join(config_dir_path(), "ghstats.config")


def check_config_dir(spnr):
  try:
    path = config_dir_path()
    # makes path recursively. returns None if already exist.
    os.makedirs(path, exist_ok=True)
    if not os.path.isfile(os.path.join(path, "ghstats.config")):
      spnr.stop()
      return create_config_file()

  except IOError:
    print("Error occured while creating config files.")

  return True


def create_config_file():
  cprint(
      "Creating config file",
      color="green",
  )

  return save_token()


def save_token():
  pat = input("please enter your github pat: ")

  headers = {
      "Authorization": f"token {pat}", 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'}

  spinner.start()
  with my_session.post('https://api.github.com/graphql', json={'query': viewer_query()}, headers=headers) as result:
    request = result
  spinner.stop()

  if request.status_code == 200:
    result = request.json()
    username = result['data']['viewer']['login']
    print(f"Saving the token for {username} in ~/.ghstats/ghstats.config")
    config["TOKEN"] = {"pat": pat}
    with open(config_file_path(), "w") as f:
      config.write(f)
    return True
  elif request.status_code == 401:
    print("The pat is not valid")
  else:
    print("error in saving the pat")

  return False


def get_saved_token():
  config.read(config_file_path())
  return config["TOKEN"]["pat"]