#!/bin/bash

RULE_POSTROUTING=$(nft list chain ip nat POSTROUTING | grep 'oifname "br-\*" accept' | wc -l)
RULE_DOCKER=$(nft list chain ip filter DOCKER-USER | grep 'iifname "br-\*" accept' | wc -l)

if [ $RULE_POSTROUTING -eq 0 ]
then
    nft insert rule ip nat POSTROUTING oifname "br-*" accept
fi
if [ $RULE_DOCKER -eq 0 ]
then
    nft insert rule ip filter DOCKER-USER iifname "br-*" accept
fi
