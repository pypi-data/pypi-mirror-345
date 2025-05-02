import json
import logging
import os
from os import PathLike
from typing import Any, Dict, List, Optional, Union

from ..util.functions import strtobool

LOG = logging.getLogger(__name__)


class GameState:
    def __init__(self, filename: PathLike):
        self.filename = filename
        self._state: Dict[str, Any] = {
            "savefile_name": os.path.split(self.filename)[-1].split(".")[0]
        }

    def save_value(
        self, key: str, value: Union[int, float, bool, str, dict, list]
    ):
        parts = key.split("__")
        state = self._state
        for idx, part in enumerate(parts):
            if idx < len(parts) - 1:
                state = state.setdefault(part, {})
            else:
                state[part] = value

    def load_value(
        self,
        key: str,
        default: Optional[Union[int, float, bool, str, dict, list]] = None,
        astype: Optional[str] = None,
    ) -> Optional[Union[int, float, bool, str, dict, list]]:
        parts = key.split("__")
        state = self._state
        for idx, part in enumerate(parts):
            if idx >= len(parts) - 1:
                # state = state.get(part)
                if state is None:
                    return default
                else:
                    state = state.get(part)
                    if state is None:
                        return default
                    if astype is not None:
                        return convert(state, astype)
                    return state

            state = state.get(part)

    def load_group(self, key: str, *more_keys: str):
        data = self._state.get(key, {})
        for key in more_keys:
            data = data.get(key, {})
        return data

    def load_from_disk(self, autosave: bool = False):
        filename = self.filename
        if autosave:
            filename = os.path.join(
                os.path.split(filename)[0], "autosave.json"
            )
        try:
            with open(filename, "r") as fp:
                self._state = json.load(fp)
        except FileNotFoundError:
            LOG.info("No saved state found!")
        except json.decoder.JSONDecodeError:
            LOG.info("No saved state found or state corrupted.")

        if autosave:
            self.filename = os.path.join(
                os.path.split(filename)[0],
                f"{self._state['savefile_name']}.json",
            )

    def save_to_disk(self, autosave: bool = False):
        filename = self.filename
        if autosave:
            filename = os.path.join(
                os.path.split(filename)[0], "autosave.json"
            )
            self.save_value("savefile_name", "autosave")
            self.save_value("player__pos_x", 5.0)
            self.save_value("player__pos_y", 5.0)
            self.save_value(
                "player__map_name", self.load_value("player__spawn_map")
            )
        else:
            self._state["savefile_name"] = os.path.split(filename)[-1].split(
                "."
            )[0]
            # Auto save file will be removed after a successful save
            try:
                os.remove(
                    os.path.join(os.path.split(filename)[0], "autosave.json")
                )
            except FileNotFoundError:
                pass

        with open(filename, "w") as fp:
            json.dump(self._state, fp, sort_keys=False, indent=4)

    def delete_keys(self, scope, keypart, exceptions):
        k2d = []
        for k in self._state[scope]:
            if keypart in k and k not in exceptions:
                k2d.append(k)
        for k in k2d:
            del self._state[scope][k]


def convert(value, astype):
    if astype == "int":
        try:
            return int(value)
        except TypeError:
            return value
    if astype == "float":
        try:
            return float(value)
        except TypeError:
            return value
    if astype == "bool":
        try:
            return strtobool(value)
        except AttributeError:
            value
    return value


def load_saved_games(save_path, save_file_name):
    os.makedirs(save_path, exist_ok=True)
    all_games = {}
    if not os.path.isdir(save_path):
        LOG.warning(f"Save folder does not exist: {save_path}")
        return all_games

    files = os.listdir(save_path)
    if not files:
        LOG.info(f"No save files found at {save_path}")
        return all_games

    if "autosave.json" in files:
        all_games["autosave"] = GameState(
            os.path.join(save_path, "autosave.json")
        )
        all_games["autosave"].load_from_disk(autosave=True)
        LOG.debug("Loading saved game from autosave.json")

    game_idx = 0
    while True:
        savegame = f"{save_file_name}{game_idx:03d}.json"
        if savegame in files:
            all_games[savegame] = GameState(os.path.join(save_path, savegame))
            all_games[savegame].load_from_disk()
            LOG.debug(f"Loading saved game from {savegame}")
        game_idx += 1
        if game_idx >= len(files):
            break

    return all_games
