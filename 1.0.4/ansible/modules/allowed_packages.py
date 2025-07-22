# ansible/modules/allowed_packages.py

utilities = [
    # From REQUIRES_ROOT
    "ufw", "gdb", "strace", "iotop", "iftop",
    "bind9utils", "cronie", "cronie-anacron", "at",

    # From REQUIRES_SUDO
    "git", "vim", "nano", "curl", "wget", "tree", "htop", "tmux", "screen",
    "zip", "unzip", "locate", "nmap", "dnsutils", "traceroute", "whois",
    "make", "gcc", "g++", "python3", "python3-pip", "openjdk-11-jdk",
    "nodejs", "npm", "golang-go", "ruby", "clang", "cmake", "perl",
    "ncdu", "jq", "yq", "xmlstarlet", "figlet", "cowsay", "toilet",
    "fortune", "neofetch", "bc", "time", "man", "net-tools", "iputils-ping"
]

#================== Allowed Packages =====================#

services = [
    "nginx", "apache2", "lighttpd",
    "mysql-server", "postgresql", "mongodb", "mariadb-server",
    "rabbitmq-server", "activemq", "zeromq", "redis-server",
    "docker.io", "podman", "containerd", "virt-manager", "libvirt-daemon",
    "jenkins", "gitlab-runner", "teamcity", "nexus", "sonarqube",
    "fail2ban", "ufw", "firewalld", "apparmor", "clamav-daemon",
    "grafana", "prometheus", "zabbix-server", "node-exporter", "telegraf", "netdata",
    "postfix", "exim4", "dovecot-core",
    "bind9", "vsftpd", "openvpn", "strongswan",
    "php-fpm", "tomcat9", "nginx-extras"
]

def is_service(pkg: str) -> bool:
    return pkg.lower() in services

def is_utility(pkg: str) -> bool:
    return pkg.lower() in utilities


