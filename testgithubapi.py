from github import Github

# First create a Github instance:

# # using username and password
# g = Github("Daibingh", "111444hdb")

# or using an access token
g = Github("c69b3bef8cedc01e270e2bf407b7013446967fc1")

# # Github Enterprise with custom hostname
# g = Github(base_url="https://{hostname}/api/v3", login_or_token="access_token")

# Then play with your Github objects:
for repo in g.get_user().get_repos():
    print(repo.name)