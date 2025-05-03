
import os
import git
import base64


from github import Github
from datetime import datetime
from subprocess import check_output, CalledProcessError

class gh():
    """
    # GitHub Automation Toolkit
    This package provides a Python class `gh` for automating common GitHub and Git tasks using the GitHub API and the Git command-line interface. This is designed to shorten and simplify github commands.

    ## why this is different and needed:
        I created it to simplify using github: many things i wish I could do in github with one command actually require several commands. For example:
        - uploading an entire folder (which beforehand wasn't initiated into github) to a repo is one command in this package: `uploadFolderFileAsCommitToRepo(...)`. In normal git this would have been surprisingly complicated: first you would need to initiate the folder, but to initiate the folder you would need to pull from the original github repo, but that would then wipe all the contents of that folder or require a merging procedure.
        - in this package you can push with one command: `uploadFolderFileAsCommitToRepo(...)`. Normally using github pushing requires 3 steps: 1) adding, committing, and pushing.
        - This package allows one to push a single file (rather than a folder) to github.
        - Ultimately, there is a reason why github is so complex: it is intended to allow multiple users to work on the same project - but when you are just a single user this complexity is burdensome.

    ## Capabilities:
        - **Repository Management**: Create and delete GitHub repositories.
        - **Branch Management**: Create, checkout, and delete branches both locally and on GitHub.
        - **Commit & Upload**: Upload a local folder to a GitHub repository as a commit, with support for automatic initialization and remote setup.
        - **Version Comparison**: Compare differences between two Git commits based on timestamps using Git's internal log and diff mechanisms.

    """

    def __init__( self, access_token ): #, repo_owner ):
        """
        **Initialize GitHub access**

        Authenticates the user using a personal access token.

        **Parameters:**
        - `access_token` *(str)*: Your GitHub personal access token.

        **Example:**
        ```python
        g = gh("your_github_access_token")
        ```
        """
        ##################
        '''
        Users need to provide github access tokens to access their github account.
        '''
        self.g = Github(access_token)
        self.user = self.g.get_user()
    
    def createRepository( self, repo_name = "new-repository" , repo_description = "This is a description for the new repository", is_private=True ):
        """
        **Create a new GitHub repository.**

        **Parameters:**
        - `repo_name` (str): Name of the repository.
        - `repo_description` (str): Description of the repository.
        - `is_private` (bool): Whether the repository is private.

        **Returns:**
        - None

        **Example:**
        ```python
        g = gh("your_github_access_token")
        g.createRepository(repo_name="test-repo", repo_description="Testing", is_private=False)
        ```
        """
        ##############
        '''
        Allows users to create a new repository in their account.
        '''
        # Create the repository
        # u#ser = self.g.get_u#ser()  # Get the authenticated u#ser
        repo = self.user.create_repo(
            name=repo_name,
            description=repo_description,
            private=is_private, #False,  # Set to True if you want the repository to be private
            auto_init=True,  # Initialize with a README file
            gitignore_template="Python",  # Optionally add a gitignore template
        )

        print(f"Repository '{repo_name}' created successfully!")


    def create_branch_in_repo(self, repo_path, branch_name):
        """
        **Create or checkout a branch in a local Git repository**

        **Parameters:**
        - `repo_path` *(str)*: Local path to the repository.
        - `branch_name` *(str)*: Name of the branch to create or checkout.

        **Example:**
        ```python
        g.create_branch_in_repo("/path/to/repo", "feature-branch")
        ```
        """
        #################
        '''
        if branch does not exist, it creates the branch and selects it.
        if the branch does exist, it ensures that is the branch that is selected.
        '''
        # def c#reate_branch_in_repo( self, repo_path, branch_name):
        #     try:
        #         # Initialize the repo object
        #         repo = git.Repo(repo_path)

        #         # Check if the branch already exists
        #         if branch_name in repo.branches:
        #             print(f"Branch '{branch_name}' already exists.")
        #         else:
        #             # Create and checkout to the new branch
        #             new_branch = repo.create_head(branch_name)
        #             new_branch.checkout()
        #             print(f"Branch '{branch_name}' created and checked out successfully.")
                
        #         return repo

        #     except git.exc.GitCommandError as e:
        #         print(f"Error: {e}")
        try:
            # Initialize the repo object
            repo = git.Repo(repo_path)

            # Check if the branch already exists
            if branch_name in [b.name for b in repo.branches]:
                print(f"Branch '{branch_name}' already exists. Checking out to it...")
                repo.git.checkout(branch_name)
            else:
                # Create and checkout to the new branch
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
                print(f"Branch '{branch_name}' created and checked out successfully.")
            
            return repo

        except git.exc.GitCommandError as e:
            print(f"Error: {e}")

    
    


    def uploadFolderFileAsCommitToRepo( self, repo_name="your_repo_name", folder_path="path/to/your/folder", commit_message="Add folder content", branch="main", force=True):
            """
            **Upload an entire folder as a commit to a GitHub repo**

            **Parameters:**
            - `repo_name` *(str)*: Name of the GitHub repository.
            - `folder_path` *(str)*: Path to the local folder.
            - `commit_message` *(str)*: Commit message.
            - `branch` *(str)*: Branch name.
            - `force` *(bool)*: Force push if conflicts occur.

            **Example:**
            ```python
            g.uploadFolderFileAsCommitToRepo(
                repo_name="test-repo",
                folder_path="./local_folder",
                commit_message="Initial upload",
                branch="main",
                force=True
            )
            ```
            """
            ####################
            '''
            uploads entire folder to a repo. If there is a problem with merging you can select “force” to ensure it works.
            '''
            
            
            repo = self.user.get_repo(repo_name)

            repo_path = os.path.abspath(folder_path)
            os.system(f'git config --global --add safe.directory {repo_path}')  # Add this line to mark the directory as safe
    
            
            ###
            def potentiallyInitiateLocalRepo():
                # Initialize the local repository if it isn't already a Git repository
                if not os.path.exists(os.path.join(repo_path, '.git')):
                    print(f"Initializing Git repository in {repo_path}")
                    repo_local = git.Repo.init(repo_path)
                else:
                    repo_local = git.Repo(repo_path)
                return repo_local
            repo_local = potentiallyInitiateLocalRepo()
            
            
            def addRemoteURL_to_local():
                # Add the remote URL if it isn't already set
                # remote_url = f"git@github.com:{u#ser.login}/{repo_name}.git"
                remote_url = f"https://github.com/{self.user.login}/{repo_name}.git"
                if 'origin' not in [remote.name for remote in repo_local.remotes]:
                    print(f"Adding remote URL: {remote_url}")
                    repo_local.create_remote('origin', remote_url)
            addRemoteURL_to_local()

            # Stage all files for commit
            repo_local.git.add(A=True)

            # Commit the files
            commit_message = "Initial commit"
            repo_local.index.commit(commit_message)

            self.create_branch_in_repo(
                repo_path = folder_path,
                branch_name = branch
                )
            
            # Push to GitHub repository
            print(f"Pushing changes to GitHub repository {repo_name}")
            repo_local.git.push('origin', branch, force=force) # 'master')  # Change 'master' to 'main' if the default branch is 'main'

            print(f"Successfully pushed to {repo_name} on GitHub.")
            
            ###

    def delete_github_repository(self, repo_name):
        """
        **Delete a GitHub repository**

        **Parameters:**
        - `repo_name` *(str)*: Name of the repository to delete.

        **Example:**
        ```python
        g.delete_github_repository("test-repo")
        ```
        """
        #########################
        """
        Delete a repository from GitHub using the GitHub API.
        
        :param repo_name: Name of the repository to delete.
        :param token: Personal access token with the necessary permissions.
        """
        try:
            repo = self.user.get_repo(repo_name)
            repo.delete()
            
            print(f"Repository '{repo_name}' has been deleted successfully!")
        
        except Exception as e:
            print(f"Error: {e}")

    def delete_github_branch( self, repo_name, branch_name ):
        """
        **Delete a branch from a GitHub repository**

        **Parameters:**
        - `repo_name` *(str)*: Repository name.
        - `branch_name` *(str)*: Name of the branch to delete.

        **Example:**
        ```python
        g.delete_github_branch("test-repo", "feature-branch")
        ```
        """
        """
        Delete a branch from a GitHub repository using the GitHub API.
        
        :param repo_name: Name of the repository.
        :param branch_name: Name of the branch to delete.
        :param token: Personal access token with the necessary permissions.
        """
        try:
            repo = self.user.get_repo(repo_name)
            ref = repo.get_git_ref(f'heads/{branch_name}')
            ref.delete()
            print(f"Branch '{branch_name}' has been deleted successfully from repository '{repo_name}'!")
        
        except Exception as e:
            print(f"Error: {e}")

    def displayDifferences( self, repo_path, time1, time2, time_choice):
        """
        **Display differences between two commits based on timestamps**

        Finds two Git commits near given times and shows their `git diff`.

        **Parameters:**
        - `repo_path` *(str)*: Path to the local repository.
        - `time1` *(datetime)*: Timestamp near the first commit.
        - `time2` *(datetime)*: Timestamp near the second commit.
        - `time_choice` *(str)*: Strategy for selecting commits - `'closest'`, `'before'`, `'after'`.

        **Example:**
        ```python
        from datetime import datetime

        t1 = datetime(2023, 5, 1, 12, 0)
        t2 = datetime(2023, 5, 2, 12, 0)

        g.displayDifferences("/path/to/repo", t1, t2, "closest")
        

        ** explaining time_choice (str):**
        Strategy for selecting which commit to use based on the provided times.
        Options:
        - 'closest': Picks the commit whose timestamp is closest to the given time (either before or after).
        - 'before': Picks the most recent commit before the given time. If no earlier commit exists, selects the earliest available commit.
        - 'after': Picks the first commit after the given time. If no later commit exists, selects the latest available commit.

        ** How It Works:**
        1. For both time1 and time2, it runs a Git command to list all commits along with their timestamps.
        2. It chooses a commit near each provided time according to the selected time_choice option.
        3. It then runs git diff between the two selected commits and prints the differences to the console.
        """


        def find_commit(repo_path, target_time, time_choice):
            """
            Finds a commit hash based on the target time and time choice.

            Args:
                repo_path (str): Path to the Git repository.
                target_time (datetime): The target time.
                time_choice (str): 'closest', 'before', or 'after'.
            
            Returns:
                str: The hash of the selected commit.
            """
            try:
                # Get a list of commits with their timestamps
                log_output = check_output(
                    ["git", "-C", repo_path, "log", "--pretty=format:%H|%at"],
                    universal_newlines=True
                ).strip().split("\n")
                
                commits = []
                for line in log_output:
                    commit_hash, timestamp = line.split("|")
                    commit_time = datetime.fromtimestamp(int(timestamp))
                    commits.append((commit_hash, commit_time))
                
                if not commits:
                    raise ValueError("No commits found in the repository.")
                
                # Sort commits by time
                commits.sort(key=lambda x: x[1])
                
                if time_choice == "closest":
                    # Find the closest commit to the target time
                    return min(commits, key=lambda x: abs((x[1] - target_time).total_seconds()))[0]
                elif time_choice == "before":
                    # Find the commit before the target time
                    for i, (commit_hash, commit_time) in enumerate(commits):
                        if commit_time >= target_time:
                            return commits[i - 1][0] if i > 0 else commits[0][0]
                    return commits[-1][0]  # If no commit is before, return the last one
                elif time_choice == "after":
                    # Find the commit after the target time
                    for commit_hash, commit_time in commits:
                        if commit_time >= target_time:
                            return commit_hash
                    return commits[-1][0]  # If no commit is after, return the last one
                else:
                    raise ValueError("Invalid time_choice. Use 'closest', 'before', or 'after'.")
            except CalledProcessError as e:
                raise RuntimeError(f"Git command failed: {e}")
            except Exception as e:
                raise RuntimeError(f"Error finding commit: {e}")

        """
        Displays all differences between two GitHub commits.

        Args:
            repo_path (str): Path to the Git repository.
            time1 (datetime): Time for the first commit.
            time2 (datetime): Time for the second commit.
            time_choice (str): 'closest', 'before', or 'after'.
        """
        try:
            # Find the commit hashes
            commit1 = find_commit(repo_path, time1, time_choice)
            commit2 = find_commit(repo_path, time2, time_choice)
            
            # Show differences between the two commits
            diff_output = check_output(
                ["git", "-C", repo_path, "diff", commit1, commit2],
                universal_newlines=True
            )
            print(f"Differences between commits {commit1} and {commit2}:\n")
            print(diff_output)
        except Exception as e:
            print(f"Error: {e}")

    def upload_file(self, repo_name, file_path, target_path=None, commit_message="Add file"):
        """
        ** Upload a single file to a GitHub repository using the GitHub API**

        This method uploads a **single file** to a GitHub repository. If the file already exists, it is updated; 
        otherwise, a new file is created. The commit includes a user-defined commit message.

        ** Parameters:**
        - `repo_name` (`str`): Full name of the repository (e.g. `"username/repo"`).
        - `file_path` (`str`): Local path to the file you want to upload.
        - `target_path` (`str`, optional): Target path inside the repo (e.g. `"folder/file.txt"`). Defaults to the file’s basename.
        - `commit_message` (`str`, optional): The commit message to use. Defaults to `"Add file"`.

        ** Example:**
        ```python
        gh.upload_file(
            repo_name="octocat/Hello-World",
            file_path="local/path/to/file.txt",
            target_path="docs/file.txt",
            commit_message="Upload documentation file"
        )
        ```
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if target_path is None:
            target_path = os.path.basename(file_path)
        
        url = f"{self.api_url}/repos/{repo_name}/contents/{target_path}"

        with open(file_path, "rb") as f:
            content = f.read()

        encoded_content = base64.b64encode(content).decode("utf-8")

        # Check if file already exists to determine if this is an update or new file
        get_resp = self.session.get(url)
        if get_resp.status_code == 200:
            sha = get_resp.json()["sha"]
            payload = {
                "message": commit_message,
                "content": encoded_content,
                "sha": sha,
            }
        else:
            payload = {
                "message": commit_message,
                "content": encoded_content,
            }

        response = self.session.put(url, json=payload)

        if response.status_code not in [201, 200]:
            raise Exception(f"Failed to upload file: {response.status_code} - {response.text}")
        
        return response.json()
