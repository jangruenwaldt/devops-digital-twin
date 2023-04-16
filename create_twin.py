import argparse

from features.cockpit.cockpit import Cockpit


def main(wipe_db, repo_url, release_branch, enable_logs):
    Cockpit.construct_digital_twin(repo_url=repo_url,
                                   release_branch_name=release_branch, debug_options={'enable_logs': enable_logs},
                                   wipe_db=wipe_db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wipe_db", type=bool, default=True, help="Wipe DB")
    parser.add_argument("--repo_url", type=str, required=True, help="Repository URL")
    parser.add_argument("--release_branch", type=str, default="master", help="Release Branch")
    parser.add_argument("--enable_logs", type=bool, default=True, help="Enable Logs")

    args = parser.parse_args()
    main(args.wipe_db, args.repo_url, args.release_branch, args.enable_logs)
