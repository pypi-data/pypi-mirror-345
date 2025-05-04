import datetime
import os
import shutil
import time
import winreg
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Union
from winreg import HKEYType

# JSONPath https://pypi.org/project/jsonpath-ng/
import jsonpath_ng
from jsonpath_ng.ext import parse as ext_parse
from pygvas import GVASFile
from pygvas import gvas_utils


# ==========================================
# Mark as dataclass so that our variable definitions syntax is not CLASS variable syntax.
# Helps avoid accidental class variables.
@dataclass
class IslandsOfInsightHelper:
    OFFLINE_SAVEFILE_NAME = "OfflineSavegame.sav"
    be_verbose = True  # class variable
    timestamp: Optional[str] = None
    timestamp_now_seconds: Optional[int] = None
    steam_install_path: Optional[Path] = None  # ioi.get_steam_install_path()
    steam_user_paths: Optional[list[Path]] = None  # ioi.find_steam_local_config_paths()
    source_sav_backup_path: Optional[Path] = None
    gvas_file: Optional[GVASFile] = None
    json_content: Optional[dict[str, Any]] = None
    player_id: Optional[str] = None
    completed_puzzle_id_set: Optional[set[int]] = None
    incomplete_puzzle_id_set: Optional[set[int]] = None
    has_last_solve_timestamp: int = 0
    has_leaderboard_timestamp: int = 0
    has_misc_status: int = 0

    # =========================================
    #
    def __init__(self):
        self.data_puzzles_db_path: str = "data/Puzzles.json"
        self.puzzlesJSON: dict | None = None

        self.data_hub_puzzles_path: str = f"data/profileHub_ext.json"
        self.profileHubJSON: dict | None = None

        self.timestamp_now_seconds = self.get_unix_timestamp_seconds()
        self.timestamp = self.get_timestamp()
        self.steam_install_path = self.find_steam_install_path()
        self.steam_user_paths = self.find_steam_local_config_paths()
        if self.be_verbose:
            # print(f"Steam Installation Path: {self.steam_install_path}")
            # print(f"User Paths: {self.steam_user_paths}")
            pass

        self.source_sav_backup_path = None
        self.gvas_file = None
        self.json_content = None
        self.player_id = None
        self.completed_puzzle_id_set = set()
        self.incomplete_puzzle_id_set = set()
        self.has_last_solve_timestamp: int = 0
        self.has_leaderboard_timestamp: int = 0
        self.has_misc_status: int = 0

    # =========================================
    #
    @staticmethod
    def get_unix_timestamp_seconds():
        return int(time.time())

    # =========================================
    #
    @staticmethod
    def get_timestamp():
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return timestamp

    # =========================================
    #
    @staticmethod
    def zone_to_name(zone: int | str):
        assert isinstance(zone, int) or isinstance(zone, str)

        if type(zone) is str:
            zone = int(zone)
        # fmt: off
        match zone:
            case -1: return "Unknown Zone"
            case 0: return "Dungeon"  # all quests, enclaves, static puzzles
            case 1: return "Lobby"  # deprecated multiplayer feature, not used by anything now
            case 2: return "Verdant Glen"
            case 3: return "Lucent Waters"
            case 4: return "Autumn Falls"
            case 5: return "Shady Wildwood"
            case 6: return "Serene Deluge"
            case 7: return "First Echoes"
            case 99: return "Unknown Zone"
            case _: return None
        # fmt: on

    # =========================================
    #
    @staticmethod
    def puzzle_type_to_name(puzzle_type: str):
        # fmt: off
        match puzzle_type:
            case "completeThePattern"		: return "PatternGrid"
            case "dungeon"					: return "Enclave"
            case "followTheShiny"			: return "WanderingEcho"
            case "fractalMatch"				: return "MorphicFractal"
            case "ghostObject"				: return "ShyAura"
            case "gyroRing"					: return "ArmillaryRings"
            case "hiddenArchway"			: return "HiddenArchway"
            case "hiddenCube"				: return "HiddenCube"
            case "hiddenRing"				: return "HiddenRing"
            case "klotski"					: return "ShiftingMosaic"
            case "levelRestrictionVolume"	: return "EntranceUnlock" # it's that glass thing that covers the jumppads to enclaves until you unlock them
            case "lightPattern"				: return "LightMotif"
            case "lockpick"					: return "PhasicDial"
            case "logicGrid"				: return "LogicGrid"
            case "match3"					: return "Match3"
            case "matchbox"					: return "MatchBox"
            case "memoryGrid"				: return "MemoryGrid"
            case "mirrorMaze"				: return "CrystalLabyrinth"
            case "musicGrid"				: return "MusicGrid"
            case "obelisk"					: return "Monolith"
            case "puzzleTotem"				: return "PillarOfInsight"
            case "racingBallCourse"			: return "FlowOrbs"
            case "racingRingCourse"			: return "GlideRings"
            case "rollingCube"				: return "RollingBlock"
            case "rosary"					: return "Skydrop"
            case "ryoanji"					: return "SentinelStones"
            case "seek5"					: return "HiddenPentad"
            case "viewfinder"				: return "SightSeer"
            case "loreFragment"				: return "LoreFragment" # not a real puzzle
            case "monolithFragment"         : return "MonolithFragment" # not a real puzzle
            case _							: return None
        # fmt: on

    # =========================================
    #

    @staticmethod
    def as_dir(path_str: str) -> Path:
        """Ensure the path behaves like a directory."""
        path = Path(path_str)
        return path if path.is_dir() else path.parent

    # =========================================
    #

    @staticmethod
    def find_steam_install_path() -> Path | None:
        """
        Use the Windows Registry to find the Steam installation path.
        """
        try:
            key: HKEYType = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Valve\Steam",
                0,
                winreg.KEY_READ,
            )
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)

            return IslandsOfInsightHelper.as_dir(install_path)

        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error accessing registry: {e}")
            return None

    # =========================================
    #

    @staticmethod
    def find_steam_local_config_paths() -> list[Path]:
        """Find all Steam 'localconfig.vdf' files using a faster glob search."""
        steam_install_path = IslandsOfInsightHelper.find_steam_install_path()
        if steam_install_path is None:
            if IslandsOfInsightHelper.be_verbose:
                print("No Steam 'localconfig.vdf' files found")
            return []

        userdata_path = steam_install_path / "userdata"
        if not userdata_path.exists() or not userdata_path.is_dir():
            if IslandsOfInsightHelper.be_verbose:
                print("No Steam 'localconfig.vdf' files found")
            return []

        # Search all '*/_config/localconfig.vdf' patterns under userdata
        local_config_files = list(userdata_path.glob("*/config/localconfig.vdf"))
        return [path for path in local_config_files if path.is_file()]

    # =========================================
    #

    @staticmethod
    def vdf_to_json(_vdf_text: str) -> dict[str, Any]:
        """
        Dummy VDF to JSON converter.
        Replace this with a real VDF parser if needed.
        """
        # This is a placeholder. You should replace it with a real VDF parser if needed.
        return {}

    # =========================================
    #

    def locate_islands_of_insight_save_game_path(self) -> Optional[Path]:

        # Method 1: Using os.environ
        # local_app_data_path = os.path.expandvars("%LOCALAPPDATA%")

        local_app_data_path: Optional[str] = os.environ.get("LOCALAPPDATA")

        if not local_app_data_path:
            if self.be_verbose:
                print("Unable to determine the AppData/Local folder.")
            return None

        save_game_path = (
            Path(local_app_data_path)
            / "IslandsofInsight/Saved/SaveGames"
            / self.OFFLINE_SAVEFILE_NAME
        )

        return save_game_path

    def rename_to_backup(self, gvas_filepath: Path):
        old_name = gvas_filepath.name
        new_name = f"{old_name}.backup.{self.timestamp}"
        new_filepath = gvas_filepath.with_name(new_name)
        if new_filepath.exists():
            raise FileExistsError(f"{new_filepath} already exists")

        # and now we rename
        gvas_filepath.rename(new_filepath)

    def rename_to_active(self, gvas_filepath: Path):
        directory = gvas_filepath.parent
        new_filepath = directory / self.OFFLINE_SAVEFILE_NAME
        if new_filepath.exists():
            raise FileExistsError(f"{new_filepath} already exists")

        # and now we rename
        gvas_filepath.rename(new_filepath)

    def create_backup_copy(self, gvas_filepath: Path):
        self.source_sav_backup_path: Path = Path(
            f"{gvas_filepath}.backup.{self.timestamp}"
        )

        # Copy the file (preserves metadata with copy2; use copy() for a simpler copy)
        shutil.copy2(gvas_filepath, self.source_sav_backup_path)
        if not self.source_sav_backup_path.exists():
            # abort
            raise FileNotFoundError(
                f"File {self.source_sav_backup_path} could not be created. Aborting."
            )

    def load_gvas_file(
        self,
        gvas_filepath: Path,
        *,
        hints_file: Optional[Path],
    ):
        assert isinstance(gvas_filepath, Path)

        if not gvas_filepath.is_file():
            raise FileNotFoundError(f"Not a file: {gvas_filepath}")

        self.gvas_file: GVASFile = GVASFile.deserialize_gvas_file(
            str(gvas_filepath), deserialization_hints=hints_file
        )
        # this will be edited in place
        self.json_content = self.gvas_file.serialize_to_json()

    def save_json_file(self, destination_filepath: Union[Path, str]):
        # call function that generates JSON
        # self.gvas_file.serialize_to_json_file(str(destination_filepath))
        gvas_utils.write_json_to_file_as_string(self.json_content, destination_filepath)

    def apply_changes_and_save_gvas_file(self, destination_filepath: Union[Path, str]):
        # call function that generates JSON
        new_gvas_file: GVASFile = GVASFile.deserialize_json(self.json_content)
        new_gvas_file.serialize_to_gvas_file(str(destination_filepath))

    # =========================================
    #
    def load_profile_hub(self):

        self.profileHubJSON = gvas_utils.load_json_from_file(self.data_hub_puzzles_path)
        assert isinstance(self.profileHubJSON, dict)
        if self.be_verbose:
            print(f"Loaded game hub details file {self.data_hub_puzzles_path}")

        # ===========================
        for zone_id in self.profileHubJSON:
            zone_data = self.profileHubJSON[zone_id]
            zone_name = zone_data["name"]
            zone_puzzle_count = zone_data["count"]
            if self.be_verbose:
                print(f"Found: {zone_name} with {zone_puzzle_count} puzzles")  # fmt: skip

    # =========================================
    #

    @staticmethod
    def generate_completed_puzzle_entry(
        puzzle_id: int, player_id: str, last_solve_time: int = 0
    ):
        # make this read only to avoid errors :)
        # fmt: off
        completed_puzzle_template = {
          "type": "StructProperty",
          "value": {
            "PlayerId": {"type": "StrProperty", "value": player_id},
            "PuzzleId": {"type": "IntProperty", "value": puzzle_id},
            "bSolved": {"type": "BoolProperty", "value": True},
            "BestScore": {"type": "IntProperty", "value": 0},
            "LastSolveTimestamp": {"type": "IntProperty", "value": last_solve_time},
            "LeaderboardTime": {"type": "FloatProperty", "value": 0.0},
            "MiscStatus": {"type": "StrProperty"},
            "bReset": {"type": "BoolProperty", "value": False},
            "bOverride_BestScore": {"type": "BoolProperty", "value": False},
            "bOverride_LastSolveTimestamp": {"type": "BoolProperty", "value": False},
            "bOverride_LeaderboardTime": {"type": "BoolProperty", "value": False},
            "bOverride_MiscStatus": {"type": "BoolProperty", "value": False},
            "bOverride_Reset": {"type": "BoolProperty", "value": False}
          }
        }
        # fmt: on
        return completed_puzzle_template

    # =========================================
    #
    def complete_all_daily_quests(self, show_completed_visual: bool):
        # grab a handle to the list of puzzle statuses
        json_status_list = self.json_content["properties"]["PuzzleStatuses"]["values"]  # fmt: skip

        if self.be_verbose:
            print(f"Started with {len(json_status_list)} tracked puzzles")

        # now we iterate over the id list for each hub
        puzzles_added = 0
        for zone_id in self.profileHubJSON:
            # print(f"Zone: {zone_id}")
            zone_data = self.profileHubJSON[zone_id]
            zone_name = zone_data["name"]
            if self.be_verbose:
                print(
                    f"Processing {zone_id=}: {zone_name} with {zone_data['count']} puzzles"
                )
            for puzzle_type, puzzle_data in zone_data.items():

                # skip the metadata; only want the zone data
                if type(puzzle_data) is not dict or not "ids" in puzzle_data:
                    continue

                # get all dailies in the hub
                puzzle_id_list = puzzle_data["ids"]
                # create a completion JSON for the puzzle
                for puzzle_id in puzzle_id_list:

                    # ignore puzzles already completed
                    if puzzle_id in self.completed_puzzle_id_set:
                        continue

                    # if a daily quest and not completed, append a completed status struct to json_status_list
                    new_completed_status = self.generate_completed_puzzle_entry(
                        puzzle_id,
                        self.player_id,
                        (self.timestamp_now_seconds if show_completed_visual else 0),
                    )
                    # this updates the loaded JSON dict in-place
                    json_status_list.append(new_completed_status)
                    puzzles_added += 1
                    self.completed_puzzle_id_set.add(puzzle_id)

        if self.be_verbose:
            print(f"Processed {puzzles_added=} puzzles")
            print(f"Ended with {len(json_status_list)} completed puzzles")

    # =========================================
    #
    def complete_all_dailies(self, show_completed_visual: Union[bool, None]):
        # used by complete_all_dailies to grab daily quest id list
        self.load_profile_hub()

        # ATM: requires that load_and_process_profile_hub() be completed
        self.complete_all_daily_quests(show_completed_visual)

    # =========================================
    #
    def harvest_player_id(self):

        # grab user id UUID from the save file
        wallet_userid_jsonpath_parser = ext_parse(
            "$.properties.Wallet.values[?(@.value.Currency.value=='coins')].value.UserId"
        )
        wallet_userid_list = wallet_userid_jsonpath_parser.find(self.json_content)
        assert type(wallet_userid_list) is list
        assert len(wallet_userid_list) == 1
        wallet_userid = wallet_userid_list[0].value
        self.player_id = wallet_userid["value"]
        if self.be_verbose:
            print(f"Found player_id: {self.player_id}")

    # =========================================
    #
    def set_sparks_balance(self, sparks_balance: int):

        assert 0 <= sparks_balance <= 100_000_000

        # direct wallet balance: $.properties.Wallet.values[?(@.value.Currency.value=='coins')].value.Balance
        wallet_balance_jsonpath_parser: jsonpath_ng.ext.parser = ext_parse(
            "$.properties.Wallet.values[?(@.value.Currency.value=='coins')].value.Balance"
        )

        wallet_balance_list = wallet_balance_jsonpath_parser.find(self.json_content)
        assert type(wallet_balance_list) is list
        assert len(wallet_balance_list) == 1
        wallet_balance = wallet_balance_list[0].value
        # now set the new value
        wallet_balance["value"] = sparks_balance
        if self.be_verbose:
            print(f"Setting sparks balance: {sparks_balance}")

    # =========================================
    #
    def collect_statistics_and_set_completed_visuals_if_requested(
        self, set_completed_visual: Union[bool, None] = None
    ):
        puzzle_status_jsonpath_parser: jsonpath_ng.ext.parser = ext_parse(
            "$.properties.PuzzleStatuses.values[*].value"
        )

        puzzle_status_list = puzzle_status_jsonpath_parser.find(self.json_content)
        assert type(puzzle_status_list) is list

        print(f"Found {len(puzzle_status_list)} existing puzzle statuses")

        self.has_last_solve_timestamp = 0
        self.has_leaderboard_timestamp = 0
        self.has_misc_status = 0
        for puzzle_status_obj in puzzle_status_list:
            puzzle_status = puzzle_status_obj.value
            # the date stamps on these imply they stopped adding when they went offline
            # "The online servers will officially shut down on October 30, 2024"
            # Found has_last_solve_timestamp=2259 puzzles
            if puzzle_status["LastSolveTimestamp"]["value"] > 0:
                self.has_last_solve_timestamp += 1

            if "PuzzleId" in puzzle_status and "bSolved" in puzzle_status:
                solved = puzzle_status["bSolved"]["value"]
                puzzle_id = puzzle_status["PuzzleId"]["value"]

                if solved is True:
                    self.completed_puzzle_id_set.add(puzzle_id)
                    # "completed" visuals are triggered by presence of a non-zero value; use "now"
                    # otherwise set to not seen with 0
                    if set_completed_visual is not None:
                        puzzle_status["LastSolveTimestamp"]["value"] = (
                            self.timestamp_now_seconds if set_completed_visual else 0
                        )

                else:
                    self.incomplete_puzzle_id_set.add(puzzle_id)

                # likewise for this value; I guess there was a plan for leaderboards
                # Found has_leaderboard_timestamp=2872 puzzles
                if puzzle_status["LeaderboardTime"]["value"] > 0:
                    self.has_leaderboard_timestamp += 1

                # some puzzles store JSON strings of data here; need to decode to read/manage, but looks case specific
                if "value" in puzzle_status["MiscStatus"]:
                    self.has_misc_status += 1

        if self.be_verbose:
            print(f"Found {len(self.completed_puzzle_id_set)} completed puzzles")
            print(f"Found {len(self.incomplete_puzzle_id_set)} uncompleted puzzles")
            print(f"Found {self.has_last_solve_timestamp=} puzzles")
            print(f"Found {self.has_leaderboard_timestamp=} puzzles")
            print(f"Found {self.has_misc_status=} puzzles")


