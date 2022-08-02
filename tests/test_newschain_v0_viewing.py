from ctypes import util
from xxlimited import new
import pytest
import brownie
from brownie import NewsChainContractv0,accounts,Contract,TestUtilityContract
import os,binascii
import traceback

@pytest.fixture(scope="module", autouse=True)
def newschain_contract(NewsChainContractv0, accounts):
    t = accounts[0].deploy(NewsChainContractv0)
    yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_view_pow_0(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')


def test_view_pow_non_existent_article(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    with pytest.raises(AttributeError):
        newschain_contract.viewer_pow(1,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')


def test_view_wrong_challenge(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[1]})
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    with pytest.raises(AttributeError):
        newschain_contract.viewer_pow(1,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')


def test_view_wrong_pow_0(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    with pytest.raises(AttributeError):
        newschain_contract.viewer_pow(0,'0x00d90da84a049451a0b9b521483892be44d507679b6c1499c7b1f68313eda64b')

def test_view_pow_0_article(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    vx = newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')
    assert vx.events["viewerEvent"]["article_id"] == 0

def test_view_pow_0_challenge(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    vx = newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')
    assert tx.events['published_article']['challenge'] == vx.events["viewerEvent"]["currentPow"]

def test_view_pow_0_expired_window(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')
    for i in range(0,10):
        accounts[0].transfer(accounts[1],1000)
    vx = newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    assert 0 == vx.events["viewerEvent"]["difficulty_level"]

def test_view_pow_3_update_level_1(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    vx0 = newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')
    assert 1 == vx0.events["viewerEvent"]["difficulty_level"]

def test_view_pow_3_update_level_1_article(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    vx = newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309') 
    assert 0 == vx.events["viewerEvent"]["article_id"]

def test_view_pow_1_level_1_insufficient(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    newschain_contract.viewer_pow(0,'0xc939f830c4ff67d6c3348211c56c606c6cc17b204997e9d4e02881ccb19c1309')
    with pytest.raises(AttributeError):
        newschain_contract.viewer_pow(0,'0xa08bee651ea141db906b6330c926455694d0d7d6876aa2af11a8dffa2e2dc051')

def test_view_pow_1_level_1_not_updates_level(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    tx = newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    assert 'updateViewLevel' not in tx.events

def test_view_pow_1_level_1_duplicated(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    dif = newschain_contract.getArticleDifficulty(tx.events['published_article']['id'])
    tx = newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    with pytest.raises(AttributeError):
        newschain_contract.viewer_pow(0,'0x0fcbc8afa2a4fabfc9d7d7df286cf06f40e58af390cc5c368fe2a33fdfc1cbf1')
    

