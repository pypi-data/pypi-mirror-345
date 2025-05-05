# Installation

`pip install racconfuncs`

# Usage

```python
from Raccon import Raccon
```

## Start

To start using the Raccon tool, create an instance of the Raccon class:

```python
raccon = Raccon()
```

To login with your credentials:

```python
raccon.login(username='your_username', password='your_password')
```
To logout:

```python
raccon.logout()
raccon.quit() # Release the memory taken up by Raccon
```

## Perform Actions

Go check in your IDE yourself.
Here is a list of functions.
```python
login(username: str, password: str)
logout()
quit()
rua(ruaid: str | list [str], capacity = 5)
getRuaList(ruaid: str)
getFollowingList()

dailycard()
sign()
newsign()
tree()

chooseWorld(world: str)
claimWorldReward()
claimAchievement()
claimQuestReward()

checkBoss(timeout = 10)
sendMessage(message: str, timeout = 10)
redeemCode(ListOfCode: str | list [str])
```