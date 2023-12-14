from .utils import payload_to_melvecs


def test_payload_to_melvecs():
    payload = "000002800000001d0056007a0085006c008c005c002900160016001f000e00070006000700050001007f0159007a0033000f000500060014000e0012001000050008000d000b0001009400f600a1008a010f01df00cc004d004d00b8005c002200150011000f0010006600a2009500e901640100005d004d004a006a002e0011000a00090013000d007400790051003c0040002800140007000f0015000d000200020003000300070046004600200013001e0017000b000600070004000200000000000000010004006b00910052000e000c000a00070002000000030000000300060001000a00040049005f0031003b001b000c00040002000200010001000200050008000c000300210039001b0028000e000800040001000000010000000100010000000000000023001d001a001c00060002000200000001000200050004000400030002000100a201380162009b0045001a0009000600060011002a0011000800100019000200a10205018e00640034000b00010000000000040014001e0005000200160007004400bc00a3001f001e00070005000400030005000d000d0005000400070002007a0185021000810015000d0009000100000006001b0037000a000b0027000a005b00c5005a0030000b000100010000000000000004000900010000000400000069009f004e001a000900020000000000000000000000030003000000030004006e012801200037000e0008000200020000000100020016001f000b0016000b00600111019300b80022000f0003000200000004000f002b00190028001200040097013c020900de00260021000f0003000200080016002500120013000e000100c201df01e100fb0046001c001700080007001700470028001b003000170002c05386b71305c633e7426ec6eb973b6e"
    melvec_length = 20
    n_melvecs = 20
    melvecs = payload_to_melvecs(payload, melvec_length, n_melvecs)

    assert melvecs.shape == (melvec_length, n_melvecs)