import argparse

from features.cockpit.cockpit import Cockpit


def main(repo_url, release_branch):
    Cockpit.fetch_twin_data(repo_url=repo_url,
                            release_branch_name=release_branch,
                            debug_options={'enable_logs': True})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_url", type=str, required=True, help="Repository URL")
    parser.add_argument("--release_branch", type=str, default="master", help="Release Branch")

    args = parser.parse_args()
    main(args.repo_url, args.release_branch)
