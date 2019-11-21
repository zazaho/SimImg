def remove_file_from_list(file,files1,files2,sims):
    tmp_files1 = []
    tmp_files2 = []
    tmp_sims = []
    for i in range(len(files1)):
        if file not in (files1[i], files2[i]):
            tmp_files1.append(files1[i])
            tmp_files2.append(files2[i])
            tmp_sims.append(sims[i])
    return tmp_files1,tmp_files2,tmp_sims


