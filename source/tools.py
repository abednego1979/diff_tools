# -*- coding: utf-8 -*-

#Python 2.7.x
import ConfigParser
import os
import datetime
import sys

from diff_patch import MyDiffPatch
from myZipFile import myZipFile
from data2QR import myCrypt
from batch_dos2unix import batch_dos2unix


def getPatch_Dir(oldDir, newDir, outPatch):
    my_diff_patch=MyDiffPatch()
    #做补丁
    buf=my_diff_patch.diff_dir_toString(oldDir, newDir, os.path.abspath(oldDir), ['.py', '.conf', '.c', '.cpp', ',h', 'txt', 'cl'])
    my_diff_patch.writePatchToFile(buf, outPatch)
    
    return

def applyPatch_Dir(patch, oldDir):
    my_diff_patch=MyDiffPatch()
    
    #打补丁
    lines=my_diff_patch.readPatchFromFile(patch)
    my_diff_patch.patch_dir_fromLines(lines, oldDir)
    
def diff_patch(opType, old_dir, new_dir, patchName):
    
    if opType=='diff':     
        #做补丁
        getPatch_Dir(old_dir, new_dir, patchName)
    elif opType=='patch':
        #打补丁
        applyPatch_Dir(patchName, old_dir)
    else:
        assert 0

    return


def main_diff(cfFile):
    old_dir=''
    new_dir=''
    
    cf = ConfigParser.ConfigParser()
    cf.read(cfFile)#读取配置文件
    old_dir='..\\'+cf.get('tipster2_diff', "old_dir")
    new_dir='..\\'+cf.get('tipster2_diff', "new_dir")
    
    while True:
        print 'Old Dir: '+old_dir
        print 'New Dir: '+new_dir
        a=raw_input('Are Directorys OK?(y/n)')
        if a=='Y' or a=='y':
            break
        elif a=='N' or a=='n':
            old_dir=raw_input('input old dir:')
            new_dir=raw_input('input new dir:')
        else:
            continue
    
    if not os.path.isabs(old_dir):
        old_dir=os.path.join(os.getcwd(), old_dir)
    if not os.path.isabs(new_dir):
        new_dir=os.path.join(os.getcwd(), new_dir)
        
    #对要比较的目录内的文件统一变换为linux格式
    bdu=batch_dos2unix()
    if bdu.checkEnv():
        bdu.setProcFileType(['py', 'txt', 'bat', 'sh'])
        bdu.dos2unix_dir(old_dir)
        bdu.dos2unix_dir(new_dir)
    else:
        print 'ERROR: can not do dos2unix'
    
    temp_patchName='patch'+datetime.date.today().strftime('%Y%m%d')
    temp_patchName=os.path.join(os.getcwd(), temp_patchName)
    
    #开始打补丁
    diff_patch('diff', old_dir, new_dir, temp_patchName)
    
    if not os.path.isfile(temp_patchName):
        print 'patch file is not created'
        return
    else:
        print 'patch file is created'
    
    #对生成的补丁文件进行压缩
    
    myZipFile().myZipFile([temp_patchName.split('\\')[-1]], 'data.zip')
    if not os.path.isfile('data.zip'):
        print 'patch file is not ziped'
        print 'a probable reason is the system date time set error'
        print 'run "sudo date -s yyyy/mm/dd" to set date.'
        return
    else:
        print 'patch file is ziped'
        
    os.remove(temp_patchName)

    pw=datetime.date.today().day*3+datetime.date.today().month
    b=myCrypt().encrypt("data.zip", pw)
    print 'trans zip file to string:'
    print b
    
    os.remove('data.zip')
    
def main_patch(cfFile):
    
    pw=datetime.date.today().day*3+datetime.date.today().month
    b=''
    try:
        with open('../../info_file.txt', 'r') as pf:
            b=pf.read()
    except:
        print 'read raw info fail'
        return
        
    b=b.rstrip('\r\n ')
    myCrypt().decrypt(b, pw, '../../data.out.zip')
    print 'recreate zip file from raw string'
    
    
    outFileList = myZipFile().myUnzipFile('../../data.out.zip')
    print 'unzip file and get file:'
    print outFileList
    os.remove('../../data.out.zip')
    
    assert len(outFileList)==1
    
    old_dir=''
        
    cf = ConfigParser.ConfigParser()
    cf.read(cfFile)#读取配置文件
    old_dir=cf.get('tipster2_patch', "old_dir")
    old_dir="/".join(old_dir.split("\\"))
    
    while True:
        print 'Old Dir: '+old_dir
        a=raw_input('Is Directory OK?(y/n)')
        if a=='Y' or a=='y':
            break
        elif a=='N' or a=='n':
            old_dir=raw_input('input old dir:')
        else:
            continue
    
    if not os.path.isabs(old_dir):
        old_dir=os.path.join(os.getcwd(), old_dir)
        
    #由于制作补丁时都是基于linux格式的（dos2unix），所以这里要将old_dir转换为linux格式
    bdu=batch_dos2unix()
    if bdu.checkEnv():
        bdu.setProcFileType(['py', 'txt', 'bat', 'sh'])
        bdu.dos2unix_dir(old_dir)
    else:
        print 'ERROR: can not do dos2unix'    
        
    diff_patch('patch', old_dir, None, outFileList[0])
    os.remove(outFileList[0])

def main(cfFile):

    if not os.path.isfile(os.path.join(os.getcwd(), cfFile)):
        print 'Config File is not exist'
        return
        
    
    while True:
        a=raw_input('Press 1 to run main_diff() or Press 2 to run main_patch() :')
        if a=='1':
            main_diff(cfFile)
            break
        elif a=='2':
            main_patch(cfFile)
            break
        else:
            pass
        
        
main('diffpatch.conf')
