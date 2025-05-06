# localized_message
## Python module to print messages according to the $LANG environment variable.

### Installing
#### Install from PyP

`pip install localized_message`

#### Install on Debian 12 and later from PyP

`pip install localized_message --break-system-packages`

#### Install from APT repositories

**As root or using sudo**

Add APT repositories:

`echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list`

Configure public signing key:

`wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg`

Upload APT repositories:

`apt update`

Install localized_message:

`apt install python-localized-message`
