import somfyrtshub
from somfyrtshub.const import CMD
from somfyrtshub.hub import ReqCoverCmd, ReqAddCover, ReqRenCover, ReqCustomCmd
import asyncio

HOST = "10.0.0.99"
PORT = 42069

hub = somfyrtshub.Hub(HOST, PORT)


# def test_toBytes():
#     assert ReqCoverCmd(12, CMD.UP)._toBytes() == b'\x0c\x00\x00\x00\x02'
#     assert ReqAddCover("Test1", 12)._toBytes(
#     ) == b'\x0c\x00\x00\x00\x00\x00\x00\x00Test1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#     assert ReqRenCover(12, "Renamed")._toBytes(
#     ) == b'\x0c\x00\x00\x00Renamed\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#     assert ReqCustomCmd(12, 10, CMD.UP, 5)._toBytes(
#     ) == b'\x0c\x00\x00\x00\n\x00\x00\x00\x02\x05'


async def _testAll():
    newCover = await hub.addCover('TestCover')
    covers = await hub.getAllCovers()
    for c in covers:
        print(c)
    await newCover.rename("TestRename")
    covers = await hub.getAllCovers()
    for c in covers:
        print(c)
    await covers[0].close()
    await hub.removeCover(newCover.remoteId)
    return await hub.getAllCovers()


def test_getAllCovers():
    covers = asyncio.run(_testAll())
    for c in covers:
        print(c)
