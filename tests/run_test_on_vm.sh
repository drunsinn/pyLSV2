#!/bin/sh
# Script to detect running VM and run tests on it

vm_name=$(VBoxManage list runningvms | grep -Po '"TNC[\w-]+')

if [ -z "$vm_name" ]; then
    echo "No running VM found."
    exit 1
fi

vm_name="${vm_name//\"/}"
vboxip1=$(VBoxManage guestproperty get "$vm_name" "/VirtualBox/GuestInfo/Net/0/V4/IP" | grep -Po '(?<=^Value: )[\d\.]+')
vboxip2=$(VBoxManage guestproperty get "$vm_name" "/VirtualBox/GuestInfo/Net/1/V4/IP" | grep -Po '(?<=^Value: )[\d\.]+')

if [ -z "$vboxip1" ] || [ -z "$vboxip2" ]; then
    echo "Could not retrieve IP addresses from VM."
    exit 2
fi
echo "IP Address 1: $vboxip1 IP Address 2: $vboxip2"

echo "Running tests on VM: $vm_name"

uv run pytest --timeout 2.0 --address $vboxip2

echo "check output for test results"

exit 0