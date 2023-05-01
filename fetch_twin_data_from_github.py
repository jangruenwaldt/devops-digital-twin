import argparse

from features.data_adapters.github_data_adapter import GitHubDataAdapter


def main(repo_url, release_branch):
    GitHubDataAdapter(repo_url, release_branch).fetch_twin_data(debug_options={'enable_logs': True})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_url", type=str, required=True, help="Repository URL")
    parser.add_argument("--release_branch", type=str, default="master", help="Release Branch")

    args = parser.parse_args()
    main(args.repo_url, args.release_branch)
