from thenewboston_node.core.utils.importing import import_from_string


def test_import_from_string():
    class_ = import_from_string('thenewboston_node.business_logic.blockchain.file_blockchain.FileBlockchain')
    from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
    assert class_ is FileBlockchain
