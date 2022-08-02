# Newschain:

[Newschain](https://newschain-frontend.pages.dev/) is an experimental platform to democratize news publication and distribution.  

Motivated by the current state of digital media: clickbait news, consumer lack of trust and censorship.  This is a non-profit experiment to understand the opportunities that the blockchain technology may offer to distribute news. 

We envision an open platform, where authors own their digital publications. That is, the ability to sell a publication, rent advertising space, as well as share its profits with their peers or audience. 

We seek a truly democratic platform.  Where the news that are relevant to the most automatically constitute the headlines of the platform. This means: an open algorithm for reporting and estimating an article relevance, as well as mechanisms to disencourage bot/trolls participation.    

Deployed as a protocol on an EVM-compatible blockchain.  News articles are posted as transactions and discovered by browsing events logs.  

# Protocol introduction

The protocol has three main sections: Publication, Viewership counting and Root/Beacon upgrade mechanism. 

## Publication

The fundamental operations of the protocol. Given a title, a cover image, an html text, and a target location, the smart contract `publish` operation registers a `published_article` event. These events represent the news articles published in the Newschain, indexed by their location and an unique fresh *id*. Once an article is registered, authors may continue/edit their articles by certifying their identity by signing a random challenge hash.

## Viewership

Perhaps the most innovative aspect of the protocol. A key limitation of blockchains lies in the throughput of transactions, as a consequence, it is not feasible to count each individual article viewed or read. We introduce a viewing protocol based on proof of work (PoW), a known blockchain mechanism, to estimate the amount of users by the viewership hash power over time. This allows us to estimate the number of readers with a low level of transactions (max 30 per hour per article), by increasing the PoW challenge difficulty accordingly. We envision to complement this mechanism by adding anti-bot mechanisms in future releases.  

## Root/Beacon contract and upgradeability

Upgrading functionality in smart contracts is an open problem. The goal of our mechanism is to be able to upgrade the protocol as well and the GUI access to the protocol, while providing backwards compatibility (at least for reading articles).           

# Building the protocol

## Requirements

Python3 https://realpython.com/installing-python/
Brownie https://eth-brownie.readthedocs.io/en/stable/install.html


## Compilation

Clone this repository 

    git clone https://github.com/ivanpostolski/newschain_cc

Build it 

    brownie compile

Running unit tests

    brownie test



