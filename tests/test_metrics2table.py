from cortexutils.metrics2table import *

def test_Metrics2Raw(mocker, requests_mock):
    # setup
    
    t = Metrics2Raw("http://mock_host", "mock_type")
    
    # before we mock, assert things we know to be true
    assert t.output() is not None

    # get ready to mock
    requests_mock.get(
        "http://mock_host",
        text="mocking",
    )
    t.output = mocker.MagicMock(name='output')
    
    # act
    t.run()
    
    # assert
    t.output.assert_called()
    
def test_ProcessNonZeros(mocker):
    # setup
    t = ProcessNonZeros("http://mock_host", "mock_type")
    
    # before we mock, assert things we know to be true
    assert t.requires() is not None
    assert t.output() is not None
    
    # get ready to mock
    t.requires = mocker.MagicMock(name='requires')    
    t.output = mocker.MagicMock(name='output')
    t.input = mocker.MagicMock(name='input')
    
    # act
    t.run()
    
    # assert
    t.output.assert_called_once()
    
    