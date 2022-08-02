import pytest
import brownie
from brownie import NewsChainContractv0,accounts,Contract,TestUtilityContract

@pytest.fixture(scope="module", autouse=True)
def newschain_contract(NewsChainContractv0, accounts):
    t = accounts[0].deploy(NewsChainContractv0)
    yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_publish_id0(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['id'] == 0

def test_publish_id1(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['id'] == 0
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[1]})
    assert tx.events['published_article']['id'] == 1
    
@pytest.mark.parametrize('title', ['', 'short', 'long'*1000])
def test_publish_challenge(newschain_contract, accounts, title):
    tx = newschain_contract.publish(title,'img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['challenge'] == '0x662ce954a41731d458592a8e203ace3aeeb0bac03c47df4824986dd12edce8a7'

def test_publish_account1(newschain_contract,accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[1]})
    assert tx.events['published_article']['challenge'] == '0x367f66ef0e32160c696a9b2f1d0a963b4828182855ca5f7694aa388e7d1a6712'

@pytest.mark.parametrize('title', ['', 'short', 'long'*1000])
def test_publish_title(newschain_contract, accounts,title):
    tx = newschain_contract.publish(title,'img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['title'] == title


def test_publish_img(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['img'] == 'img'

@pytest.mark.parametrize('text', ['', 'short', 'long'*1000])
def test_publish_text(newschain_contract, accounts,text):
    tx = newschain_contract.publish('title','img',text,'ar',{'from':accounts[0]})
    assert tx.events['published_article']['article'] == text


def test_publish_author(newschain_contract, accounts):
    tx = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    assert tx.events['published_article']['author'] == accounts[0].address

def test_publish_continue_id(newschain_contract,accounts):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    tx_continue = newschain_contract.continue_article(0,'change',"0x6a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})
    assert tx_continue.events['article_continuation']['id'] == 0

def test_publish_continue_changes(newschain_contract,accounts):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    tx_continue = newschain_contract.continue_article(0,'change',"0x6a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})
    assert tx_continue.events['article_continuation']['changes'] == 'change'

def test_publish_continue_challenge(newschain_contract,accounts):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    tx_continue = newschain_contract.continue_article(0,'change',"0x6a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})
    assert tx_continue.events['article_continuation']['challenge'] == '0x41a9c7e043b7068700385b9c325ec011b63f2cc19ec034436efe0ea2f6d3e484'

def test_publish_continue_wrong_signature(newschain_contract,accounts):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    with pytest.raises(AttributeError):
        tx_continue = newschain_contract.continue_article(0,'change',"0x0a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})

@pytest.mark.parametrize('id', [1, 2])
def test_publish_continue_wrong_id(newschain_contract,accounts,id):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    with pytest.raises(AttributeError):
        tx_continue = newschain_contract.continue_article(id,'change',"0x6a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})
 

@pytest.mark.parametrize('id', [2**256, 2**256 + 1])
def test_publish_continue_wrong_id_overflow(newschain_contract,accounts,id):
    tx_publish = newschain_contract.publish('title','img','text','ar',{'from':accounts[0]})
    with pytest.raises(OverflowError):
        tx_continue = newschain_contract.continue_article(id,'change',"0x6a227af3a9218ab189eacb04f1ca5a474726f3a44c5939a018bee88b6077c674500a5c6e637eedc748c6748e0e8e5238bfbf43e057c33e7e441c1437d85b6f031b",{'from':accounts[0]})
    
def test_donate_access(newschain_contract,accounts):
    key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    fresh_acc = accounts.add(private_key=key)
    newschain_contract.donateAccess(fresh_acc,key,{'from':accounts[0],'value':1000})
    assert fresh_acc.balance() == 1000

def test_donate_access_unauthorized(newschain_contract,accounts):
    key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    fresh_acc = accounts.add(private_key=key)
    with pytest.raises(AttributeError):
        newschain_contract.donateAccess(fresh_acc,key,{'from':accounts[1],'value':1000})
    
    assert fresh_acc.balance() == 0

def test_donate_access_no_funds(newschain_contract,accounts):
    key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    fresh_acc = accounts.add(private_key=key)
    with pytest.raises(ValueError):
        newschain_contract.donateAccess(fresh_acc,key,{'from':accounts[0], 'value':1e25})
    
    assert fresh_acc.balance() == 0




# For some reason this test breaks brownie coverage analysis 
@pytest.mark.skip_coverage
def test_donate_access_no_gas(newschain_contract,accounts):
    key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    fresh_acc = accounts.add(private_key=key)
    with pytest.raises(KeyError):
        newschain_contract.donateAccess(fresh_acc,key,{'from':accounts[0], 'value':1e17, 'gas_limit':50000})
    
    assert fresh_acc.balance() == 0


