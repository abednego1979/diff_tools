# -*- coding: utf-8 -*-
#Python 2.7.x
import diff_match_patch
import os
import shutil
import filecmp
import chardet


__metaclass__ = type
    
    
class MyDiffPatch():

    def formatPath(self, path):
        return "/".join(path.split("\\"))
    
    def readFile2UnicodeBuf(self, filename):
        readstring=None
        oldCodingType=None
        try:
            with open(filename, 'rb') as pf:
                readstring=pf.read()
                
                if readstring:
                    if isinstance(readstring, unicode):
                        oldCodingType='unicode'
                    else:
                        oldCodingType=chardet.detect(readstring)['encoding']
                        readstring=readstring.decode(oldCodingType)
                        if not isinstance(readstring, unicode):
                            assert 'File content decode fail'
                else:
                    return '',None
        except:
            print 'ERROR: read file fail:'+filename
            return None,None
        return readstring,oldCodingType

    def diff_file_toString(self, old_File, new_File):
        if not os.path.isfile(old_File) or not os.path.isfile(new_File):
            print 'ERROR: input file name error'
            print  old_File
            print  new_File
            return
            
        old_string, oldfilecoding=self.readFile2UnicodeBuf(old_File)
        new_string, newfilecoding=self.readFile2UnicodeBuf(new_File)
        if os.path.getsize(old_File):
            assert oldfilecoding
            #assert oldfilecoding==newfilecoding or newfilecoding == 'ascii', 'ERROR: file coding diff: %s : %s : %s' % (new_File, oldfilecoding, newfilecoding)
            pass
              
        diff_obj = diff_match_patch.diff_match_patch()
        diffs = diff_obj.diff_main(old_string, new_string)
        patches=diff_obj.patch_make(diffs)
        patches_text=diff_obj.patch_toText(patches)
        
        return patches_text
    
    def patch_file_fromString(self, patches_text, old_File):
        if not os.path.isfile(old_File):
            print 'ERROR: input file name error'
            print  old_File
            return        
        
        old_string, oldfilecoding=self.readFile2UnicodeBuf(old_File)
        if not oldfilecoding:
            oldfilecoding='utf-8'

        diff_obj = diff_match_patch.diff_match_patch()
        patches=diff_obj.patch_fromText(patches_text)
        
        patched_res=diff_obj.patch_apply(patches, old_string)
        
        someError=False
        for index,item in enumerate(patched_res[1]):
            if not item:
                someError=True
                print 'ERROR: patch fail at:'
                print patches[index]
        
        if someError:
            print 'ERROR: some fuzz in patch'
            

        new_string=patched_res[0]
        if oldfilecoding == 'unicode':
            new_string=new_string.encode(oldfilecoding)
        else:
            new_string=new_string.encode('utf-8')
        
        return new_string,someError
    
    def patch_file_savefile(self, patches_text, old_File, new_file):
        
        if os.path.isfile(old_File) and os.path.isfile(new_file):
            new_string,someError=self.patch_file_fromString(patches_text, old_File)
            if someError:
                shutil.copyfile(new_file, new_file+'.raw')
            try:
                with open(new_file, 'wb') as pf:
                    pf.write(new_string)
            except:
                print 'ERROR: write to new file error'
        else:
            print 'ERROR: some file lost'
            print old_File
            print new_file
    
           
    def _get_diff_files_(self, dcmp):
        temp=[]
        for name in dcmp.diff_files:
            temp+=[[name, dcmp.left, dcmp.right]]
        for sub_dcmp in dcmp.subdirs.values():
            temp+=self._get_diff_files_(sub_dcmp)
        return temp
    
    def _get_del_files_(self, dcmp):
        temp=[]
        for name in dcmp.left_only:
            temp+=[[name, dcmp.left, dcmp.right]]
        for sub_dcmp in dcmp.subdirs.values():
            temp+=self._get_del_files_(sub_dcmp)
        return temp
    
    def _get_add_files_(self, dcmp):
        temp=[]
        for name in dcmp.right_only:
            temp+=[[name, dcmp.left, dcmp.right]]
        for sub_dcmp in dcmp.subdirs.values():
            temp+=self._get_add_files_(sub_dcmp)
        return temp
        
    
    def diff_dir_toString(self, old_dir, new_dir, old_base_dir, fileType=[]):
        x=filecmp.dircmp(os.path.abspath(old_dir), os.path.abspath(new_dir))

        #del_file_list=x.left_only
        #add_file_list=x.right_only
        del_file_list=self._get_del_files_(x)
        add_file_list=self._get_add_files_(x)
        diff_file_list=self._get_diff_files_(x)
        
        temp_del_file_list=[]
        temp_add_file_list=[]
        temp_diff_file_list=[]
        
        for postfix in fileType:
            temp_del_file_list+=[item for item in del_file_list if item[0].endswith(postfix)]
            temp_add_file_list+=[item for item in add_file_list if item[0].endswith(postfix)]
            temp_diff_file_list+=[item for item in diff_file_list if item[0].endswith(postfix)]
            
        del_file_list=temp_del_file_list
        add_file_list=temp_add_file_list
        diff_file_list=temp_diff_file_list
        
        #有修改的文件
        res_buf=''
        for diff_item in diff_file_list:
            res_buf+='---modify---'+os.path.join(diff_item[1], diff_item[0]).replace(old_base_dir, '')+'\n'
            ds=self.diff_file_toString(os.path.join(diff_item[1], diff_item[0]), os.path.join(diff_item[2], diff_item[0]))
            res_buf+=ds
            print os.path.join(diff_item[1], diff_item[0]).replace(old_base_dir, '')+' modified'
            
        for del_item in del_file_list:
            res_buf+='---del---'+os.path.join(del_item[1], del_item[0]).replace(old_base_dir, '')+'\n'
            print os.path.join(del_item[1], del_item[0]).replace(old_base_dir, '')+' deleted'
        
        for add_item in add_file_list:
            if os.path.isfile(os.path.join(add_item[2], add_item[0])):
                res_buf+='---add---'+os.path.join(add_item[1], add_item[0]).replace(old_base_dir, '')+'\n'
                #先在old_dir目录下创建一个空的文件
                try:
                    with open(os.path.join(add_item[1], add_item[0]), 'wb') as pf:
                        pass
                except:
                    print 'ERROR: create file fail'
                    
                ds=self.diff_file_toString(os.path.join(add_item[1], add_item[0]), os.path.join(add_item[2], add_item[0]))
                res_buf+=ds
                print os.path.join(add_item[1], add_item[0]).replace(old_base_dir, '')+' added'
                
                #删除刚才临时创建的文件
                os.remove(os.path.join(add_item[1], add_item[0]))
            else:
                #新目录增加了一个目录
                res_buf+='---adddir---'+os.path.join(add_item[1], add_item[0]).replace(old_base_dir, '')+'\n'
                
                #在旧目录下临时创建这个文件夹
                os.mkdir(os.path.join(add_item[1], add_item[0]))
                
                print os.path.join(add_item[1], add_item[0]).replace(old_base_dir, '')+' added'
                
                #对新旧目录进行补丁比较
                res_buf+=self.diff_dir_toString(os.path.join(add_item[1], add_item[0]), os.path.join(add_item[2], add_item[0]), old_base_dir, fileType)

                #删除临时创建的文件夹
                os.rmdir(os.path.join(add_item[1], add_item[0]))

        return res_buf
    
    def patch_dir_fromLines(self, patches_lines, old_dir):
        #打开文件并找出各个文件的分界线
        cur_type='Unknown'
        cur_file=''
        
        blocks=[]
        for line in patches_lines:
            if line.startswith('---modify---'):
                block=['m', line[len('---modify---'):].rstrip('\n'), '']#type,filename,buf
                blocks.append(block)
            elif line.startswith('---del---'):
                block=['d', line[len('---del---'):].rstrip('\n'), '']
                blocks.append(block)
            elif line.startswith('---add---'):
                block=['a', line[len('---add---'):].rstrip('\n'), '']
                blocks.append(block)
            elif line.startswith('---adddir---'):
                block=['ad', line[len('---adddir---'):].rstrip('\n'), '']
                blocks.append(block)                
            else:
                blocks[-1][2]+=line
        
        for block in blocks:
            if block[0]=='m':
                #对文件fileName使用temp_buf进行modify
                pathfile=old_dir+block[1]
                pathfile="/".join(pathfile.split("\\"))
                self.patch_file_savefile(block[2], pathfile, pathfile)
                print 'modify file:'+pathfile
            elif block[0]=='d':
                #删除new_dir中的对应文件
                pathfile=old_dir+block[1]
                pathfile="/".join(pathfile.split("\\"))
                
                if os.path.isfile(pathfile):
                    try:
                        os.remove(pathfile)
                        print 'remove file:'+pathfile
                    except:
                        print 'ERROR: remove file fail:'+pathfile
                else:
                    #删除的是目录
                    try:
                        shutil.rmtree(pathfile,True)
                        print 'remove dir:'+pathfile
                    except:
                        print 'ERROR: remove dir fail:'+pathfile
            elif block[0]=='a':
                #先在old_dir目录下创建一个空的文件
                pathfile=old_dir+block[1]
                pathfile="/".join(pathfile.split("\\"))
                try:
                    with open(pathfile, 'wb') as pf:
                        pass
                except:
                    print 'ERROR: create file fail'
                    
                #然后打补丁
                self.patch_file_savefile(block[2], pathfile, pathfile)
                print 'add file:'+pathfile
            elif block[0]=='ad':
                #在old_dir目录下创建空文件夹
                path=old_dir+block[1]
                path="/".join(path.split("\\"))
                os.mkdir(path)

                print 'add dir:'+path
            else:
                assert 0

        
        return
    
    
    def writePatchToFile(self, buf, filename):
        filename=self.formatPath(filename)
        try:
            with open(filename, 'wb') as pf:
                pf.write(buf)
        except:
            print 'ERROR: write patch to file fail'
        return
    
    def readPatchFromFile(self, filename):
        filename=self.formatPath(filename)
        lines=[]
        try:
            with open(filename, 'rb') as pf:
                lines = pf.readlines()
        except:
            print 'ERROR: read patch from file fail'
        return lines

    

            