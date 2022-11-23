def inputLink():
    list = []

    print('NHAP "stop" KHI MUON DUNG')
    while True:
        val = input('Enter link: ')
        if val == 'stop':
            print('====== KET THUC ======')
            break
        list.append(val)
    return list