import argparse

from features.twins.twin_builder import TwinBuilder


def main(repo_url, wipe_db, enable_logs):
    TwinBuilder.construct_from_github_data_repo(repo_url=repo_url, debug_options={'enable_logs': enable_logs},
                                                wipe_db=wipe_db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_url", type=str, required=True, help="Twin data repository URL")
    parser.add_argument("--wipe_db", type=bool, default=True, help="Wipe DB")
    parser.add_argument("--enable_logs", type=bool, default=True, help="Enable Logs")

    args = parser.parse_args()
    main(args.repo_url, args.wipe_db, args.enable_logs)
