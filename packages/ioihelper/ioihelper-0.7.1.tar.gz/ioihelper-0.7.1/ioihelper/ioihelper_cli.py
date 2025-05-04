import argparse
import sys
from pathlib import Path

from ioihelper.ioihelper_core import IslandsOfInsightHelper


# =========================================
# main code for command line
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Modify an Islands of Insight .sav file (OfflineSavegame.sav) as requested. Will prints out some gameplay statistics if no modifications are requested."
    )
    parser.add_argument(
        "--backup_old_and_use_new",
        action="store_true",
        help="Without this flag your edits will not go into effect. This backs up the original file by giving it a timestamp and renames the modified file so it will be loaded by Islands of Insight.",
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default=None,
        help="Path to the Islands of Insight save file. If not present, looks for your save file installation.",
    )
    parser.add_argument(
        "--hints_file",
        type=str,
        default=None,
        help="Path to optional deserialization hints (JSON) file. AFAIK, Islands doesn't need one. See the pygvas documentation for more information.",
    )
    parser.add_argument(
        "--set_sparks_balance",
        type=int,
        default=None,  # 10_000_000,
        help="Sets the Sparks (currency) in your account for purchasing cosmetics. The ones you don't get through mainline and zone progression.",
    )
    parser.add_argument(
        "--show_completed_visuals",
        type=bool,
        default=None,
        help="Permanently enable/disable visuals cues for puzzle completion. Persists beyond the current play session.",
    )
    parser.add_argument(
        "--save_json",
        action="store_true",
        help="Save JSON save game files for both before and after modifications. These will land next to the indicated save game source file.",
    )
    parser.add_argument(
        "--complete_all_dailies",
        action="store_true",
        help="Mark ALL dailies completed. This will grant all the progression cosmetics, but the game will be less fun to play. It does NOT affect the meta puzzles or enclaves.",
    )

    return parser.parse_args()


# =========================================
#
def main():
    args = parse_arguments()

    try:
        ioi_helper = IslandsOfInsightHelper()
        input_file = (
            args.input_file
            if args.input_file is not None
            else ioi_helper.locate_islands_of_insight_save_game_path()
        )

        print(
            f"Working with save file: {input_file}\n\tand hints file: {args.hints_file}"
        )

        if not input_file.is_file():
            raise ValueError(f"Not a file: {input_file}")

        hints_file = Path(args.hints_file) if args.hints_file is not None else None
        if hints_file is not None and not hints_file.is_file():
            raise ValueError(f"Invalid hints file: {hints_file}")

        ioi_helper.load_gvas_file(input_file, hints_file=hints_file)

        if args.save_json:
            ioi_helper.save_json_file(
                f"{input_file}.{ioi_helper.timestamp}.start.json",
            )

        data_were_modified = False

        # always, in case we will complete all dailies
        ioi_helper.harvest_player_id()

        if args.set_sparks_balance:
            ioi_helper.set_sparks_balance(args.set_sparks_balance)
            data_were_modified = True

        # we always gather the stats because used by complete_all_dailies for accounting.
        ioi_helper.collect_statistics_and_set_completed_visuals_if_requested(
            set_completed_visual=args.show_completed_visuals
        )
        if args.show_completed_visuals is not None:
            data_were_modified = True

        if args.complete_all_dailies:
            ioi_helper.complete_all_dailies(
                show_completed_visual=args.show_completed_visuals
            )
            data_were_modified = True

        if data_were_modified:
            if args.save_json:
                ioi_helper.save_json_file(
                    f"{input_file}.{ioi_helper.timestamp}.end.json",
                )

            # and for the big finale, we overwrite the original file? Or do we make a new one and let the user rename them?
            processed_gvas_file = Path(f"{input_file}.{ioi_helper.timestamp}.sav")
            ioi_helper.apply_changes_and_save_gvas_file(processed_gvas_file)

        if data_were_modified and args.backup_old_and_use_new:
            ioi_helper.rename_to_backup(input_file)
            ioi_helper.rename_to_active(processed_gvas_file)

        print(f"Processed the file '{input_file}'.")

    except Exception as e:
        print(f"Error processing input_file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
