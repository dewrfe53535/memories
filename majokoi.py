import re
import librosa

def translator(string,text_actionflag = 0,bg_actionflag = 0,face_flag = 0,shakeflag= 0 ):
    global time_prefix
    global nowtextsize

    if r'function StoryRun()' in string or r'this.batch()' in string or r'this.game_end()' in string or 'title_change' in string or 'trophy_unlock' in string or 'music_release' in string or 'flag_set' in string or 'file_change' in string or r'txtwin_proc' in string or r'txtwin_type' in string and 'this.bg_print_anime' in string or 'log_set' in string:
        return None
    if 'this.bg_print_ex' in string:
        bgname = re.findall(r'this.bg_print_ex\("(.*?)", (.*?), (.*?), (.*?)\)', string)[0]
        bgname = list(bgname)
        def prebgtemp():
            if bg_actionflag ==1 :
                return bg_template_sepia.format(bgname[0])
            else:
                return bg_template.format(bgname[0])
        nowde = prebgtemp()
        if bg_actionflag == 1:
            bgname[0] = bgname[0]+ '_sepia'
        time_prefix = int(bgname[1]) / 100
        if bgname[3] == '14':
            return [1, nowde,
                    'scene %s  onlayer background with Dissolve(%s)\n    $ camera_reset() \n    $ camera_move(0,0,600,0,45)\n' % (bgname[0],time_prefix)]
        elif bgname[3] == '20':
            return [1, nowde, 'scene %s onlayer background at bg_moverl with Dissolve(%s) \n    $ camera_reset() \n' % (bgname[0],time_prefix)]
        elif bgname[2] == '14':
            cont = 'scene {0} onlayer background with ImageDissolve(im.Tile("images/pc_effect/MASK04.png"), {1}, 2)  \n'.format(bgname[0], time_prefix)
            return [1, nowde, cont]
        elif bgname[2] == '12':
            cont = 'scene {0} onlayer background with ImageDissolve(im.Tile("images/pc_effect/MASK02.png"), {1}, 2)  \n'.format(bgname[0], time_prefix)
            return [1, nowde, cont]
        elif bgname[2] == '10':
            time_prefix = int(bgname[1]) / 100
            cont = 'scene {0} onlayer background with ImageDissolve(im.Tile("images/pc_effect/MASK01.png"), {1}, 2)  \n'.format(bgname[0], time_prefix)
            return [1, nowde, cont]
        elif bgname[3] == '7':
            return [1, nowde, 'scene %s onlayer background at bkid_7 with Dissolve(%s) \n    $ camera_reset() \n' % (bgname[0],time_prefix)]
        elif bgname[3] == '15':
            return [1,nowde, 'scene %s onlayer background at bkid_15 with Dissolve(%s) \n    $ camera_reset() \n' % (bgname[0],time_prefix)]
        else:
            #print(bgname[3])
            return [1, prebgtemp(), 'scene %s onlayer background with dissolve  \n    $ camera_reset() \n' % bgname[0]]
    elif 'bgm_play' in string:
        return [0, mu_template.format(re.findall(r'bgm_play\((.*?),', string)[0].zfill(3))]
    elif 'speaker_name' in string:
        return [0, '"%s"' % re.findall(r'this.speaker_name\("(.*?)"', string)[0]]
    elif 'this.maintxt_print' in string:
        text2 = re.findall(r'maintxt_print\("(.*?)"', string)[0].replace('#n', '\\n')
        try:
            text2size = re.findall(r'#Scale\[(.*?)\]', string)[0]
            newsize = nowtextsize * float(text2size)
            text2 = re.sub(r'#Scale\[.*?\]', '{size=%s}' % int(newsize), text2) + '{/size}'
        except IndexError:
            pass
        text2 = text2.replace('[', '\[')
        text2 = text2.replace(']', '\]')
        if text_actionflag == 1:
            return [19,text2]
        if face_flag == 1:
            return [23,text2]
        return [0, '"%s"\n' % text2]
    elif 'bgm_stop' in string:
        return [0, 'stop music fadeout 1.0\n']
    elif 'voice_play(' in string:
        volist = re.findall(r'voice_play\((.*?), (.*?)\)', string)[0]
        all_voice.append('D:\\renpy_working\\majo_koi\\game\\voice\\{0}\\{1}.ogg'.format(volist[0], volist[1].zfill(6)))
        return [0, 'voice  ' + vo_template.format(volist[0], volist[1].zfill(6)) + '', volist]
    elif 'voice_play_pan' in string:
        volist = re.findall(r'voice_play_pan\((.*?), (.*?),', string)[0]
        all_voice.append('D:\\renpy_working\\majo_koi\\game\\voice\\{0}\\{1}.ogg'.format(volist[0], volist[1].zfill(6)))
        return [0, 'voice  ' + vo_template.format(volist[0], volist[1].zfill(6)) + '', volist]
    elif 'bg_print(' in string:
        bgname = re.findall(r'this.bg_print\("(.*?)", (.*?)\)', string)[0]
        if shakeflag ==1:
            return [13, bg_template.format(bgname[0]), 'scene %s onlayer background at sshake\n    ' % bgname[0],
                    bgname[1]]
        if bg_actionflag == 0:
            return [13, bg_template.format(bgname[0]), 'scene %s onlayer background\n    ' % bgname[0], bgname[1]]
        elif bg_actionflag ==1:
            return [13, bg_template_sepia.format(bgname[0]), 'scene %s_sepia onlayer background\n    ' % bgname[0], bgname[1]]
    elif 'bg_print2(' in string: #该函数原本并不存在，为方便而设置
        bgname = re.findall(r'this.bg_print2\("(.*?)", (.*?)\)', string)[0]
        return [13, bg_template.format(bgname[0]), 'scene %s onlayer background\n    ' % bgname[0], bgname[1],-1]

    elif 'this.wait_time' in string:
        time = re.findall(r'wait_time\((.*?)\)', string)[0]
        time = (int(time) - time_prefix) / 100
        if time_prefix != 0:
            time_prefix = 0
        if time > 0:
            return [0, 'pause ' + str(float(time)) + '\n']
        return None
    elif 'ezface_app' in string:
        facecode = re.findall(r'ezface_app\("(.*?)", "(.*?)"\)', string)[0]
        face = facecode[0] + '_' + facecode[1]
        return [2, face_template.format(face), face, '    show side {0}\n'.format(face)]
    elif 'ezface_del(' in string:
        return [3, 'hide side ']
    elif 'strse_play(' in string:
        sid = re.findall(r'strse_play\((.*?),', string)[0].zfill(6)
        return [15, 'play sound "sound/{0}.ogg"\n'.format(sid), sid]
    elif 'this.strse_wait(' in string:
        return [14]
    elif 'strse_loop(' in string:
        return [16]
    elif 'strse_stop(' in string:
        return[0,'$renpy.music.stop(\'loopback_sound\' )\n']
    elif 'ezchara_nextstate(' in string:
        var3 = re.findall(r'ezchara_nextstate\("(.*?)", "(.*?)", "(.*?)"', string)[0]
        return [4, chara_template.format('{0}_{1}_{2}'.format(var3[0], var3[1], var3[2]), var3[1],getcharaypos(var3[1],var3[2])),
                [var3[0], var3[1], var3[2]],
                var3]
    elif 'ezchara_nextstate4' in string:
        var3 = re.findall(r'ezchara_nextstate4\("(.*?)", "(.*?)", "(.*?)"', string)[0]
        return [4, chara_template.format('{0}_{1}_{2}'.format(var3[0], var3[1], var3[2]), var3[1],getcharaypos(var3[1],var3[2])),
                [var3[0], var3[1], var3[2]],
                var3]
    elif 'ezchara_del(' in string:
        echara = re.findall(r'ezchara_del\("(.*?)",', string)[0]
        return [5, 'hide %s \n', echara]
    elif 'ezchara_pos_move' in string:
        chapos = re.findall(r'ezchara_pos_move\("(.*?)", (.*?),', string)[0]
        posn = int(chapos[1])
        return [6, chapos[0], posn]
    elif 'ezchara_pos_app(' in string:
        chapos = re.findall(r'ezchara_pos_app\("(.*?)", "(.*?)", "(.*?)", (.*?), (.*?), ', string)[0]
        return [7, chapos]
    elif 'after_effect_bg("' in string:
        bgname = re.findall(r'effect_bg\("(.*?)"', string)[0]
        return [1, bg_template.format(bgname), 'scene transparent with dissolve\n    scene %s onlayer background with fade\n' % bgname]
    elif 'chara_all_reset' in string:
        return [8]
    elif 'ezchara_pos_app2' in string:
        chapos = re.findall(r'ezchara_pos_app2\("(.*?)", "(.*?)", "(.*?)", "(.*?)", "(.*?)", (.*?), (.*?),', string)[0]
        return [7, [chapos[0], chapos[1], chapos[2], chapos[5], chapos[6]]]
    elif 'nextstate3' in string:
        var3 = re.findall(r'nextstate3\("(.*?)", "(.*?)", "(.*?)", "(.*?)", "(.*?)", (.*?), (.*?)', string)[0]
        return [4, chara_template.format('{0}_{1}_{2}'.format(var3[0], var3[1], var3[2]), var3[1],getcharaypos(var3[1],var3[2])),
                [var3[0], var3[1], var3[2]],
                var3]
    elif 'nextstate6' in string:
        var3 = re.findall(r'ezchara_nextstate6\("(.*?)", "(.*?)", "(.*?)"', string)[0]
        return [4, chara_template.format('{0}_{1}_{2}'.format(var3[0], var3[1], var3[2]), var3[1],getcharaypos(var3[1],var3[2])),
                [var3[0], var3[1], var3[2]],
                var3]
    elif 'subtitle_set' in string:
        var1 = re.findall(r'subtitle_set\("(.*?)"', string)[0]
        return [0, '$ renpy.notify("%s")\n'%var1]
    elif 'movie_play' in string:
        var1 = re.findall(r'movie_play\("(.*?)", (.*?)\)', string)[0]
        if int(var1[1]) == 0:
            if 'book' not in var1[0]:
                return [0, 'play movie  "movie/%s.webm"\n'%var1[0]]
            else:
                return [0, '$ renpy.movie_cutscene("movie/%s.webm", stop_music=False)\n' % var1[0]]
        if int(var1[1]) == 1:
            if '034' in var1[0]:
                return [0,'if not config.skipping:\n        show {0} onlayer  animatedeffect\n'.format(var1[0])]
            return None
    elif 'fg_print(' in string:
        var1 = re.findall(r'fg_print\("(.*?)", (.*?)\)', string)[0]
        time_prefix = float(int(var1[1]) / 100)
        var2 = 'show {0} onlayer  effect with Dissolve({1})\n'.format(var1[0], float(int(var1[1]) / 100))
        if shakeflag ==1:
            var2 = 'show {0} onlayer  effect at sshake with Dissolve({1})\n'.format(var1[0], float(int(var1[1]) / 100))
            return [0, var2]
        return [0, var2]
    elif 'fg_delete(' in string:
        var1 = re.findall(r'fg_delete\("(.*?)", (.*?)\)', string)[0]
        time_prefix = float(int(var1[1]) / 100)
        var2 = 'hide {0} onlayer  effect with Dissolve({1})\n'.format(var1[0], float(int(var1[1]) / 100))
        return [0,var2]
    elif 'fg_all_delete(' in string:
        var = 'scene transparent  onlayer effect with dissolve\n    $ camera_reset() \n'
        return [0,var]
    elif 'this.camera_act(' in string:
        var1 = re.findall(r'camera_act\((.*?), (.*?), (.*?), (.*?), (.*?)\)', string)[0]
        if int(var1[0]) == 0 and int(var1[1]) == 0 and int(var1[2]) == 0:
            var2 = abs(int(var1[3])) * 12
            var3 = int(var1[4]) / 100
            return [0, '$ camera_move(0,0,{0},0,{1})\n'.format(var2, var3)]
    elif 'movie_end(' in string:
        return [0, 'scene onlayer animatedeffect\n']
    elif 'camera_action(' in string:
        var1 = re.findall(r'camera_action\((.*?), "(.*?)"', string)[0]
        if var1[1] == 'TEXT' or var1[1] == 'font' or var1[1] =='FONT':
            return [18,var1[0]]
        elif var1[1] == 'FACE' or var1[1] == 'Face' or var1[1] =='RenSh':
            return [22,var1[0]]
        else:
            return [20,var1]
    elif 'sepia_change(' in string:
        var1 = re.findall(r'sepia_change\((.*?)\)', string)[0]
        return [21,var1]
    elif 'blackout_start(' in string:
        var1 =re.findall(r'blackout_start\((.*?), (.*?), (.*?)\)', string)[0]
        var2type = 'white' if var1[1] == '0' else 'black'
        waittime  = str(int(var1[2])/100)
        time_prefix = float(waittime)
        if var1[0] == '2':
            var3 = 'scene %s onlayer blackout with Dissolve(%s)\n'%(var2type,waittime)
            return [0,var3]
    elif 'blackout_end(' in string:
        var1 =re.findall(r'blackout_end\((.*?), (.*?)\)', string)[0]
        time_prefix = int(var1[1])/100
        if var1[0] == '2':
            return [0,'scene transparent onlayer blackout with Dissolve(%s)\n'%(int(var1[1])/100)]
    elif 'after_effect_set(' in string:
        return [24]
    elif '$cu$st$om' in string:
        return [25,string[9:]+'\n']
    elif 'ut_flash(' in string:
        var1 =re.findall(r'blackout_flash\((.*?), .*?, (.*?)\)', string)[0]
        var1type = var1[0]
        var1time = var1[1]
        if var1type == '2' or var1type == '1' or var1type == '0':#似乎只是线性时间不同，忽略
            var1time = int(var1time)/200
            backstr = 'show white onlayer blackout with Dissolve({0})\n    hide white onlayer blackout with Dissolve({0})\n'.format(var1time)
            return [0,backstr]
    elif 'display_shake(' in string:
        if 'display_shake(1)' in string:
            return [26]
        elif shakeflag ==1:
            return [27]
    elif 'shake_stop(' in string:
        return [27]
    else:
        return None
        #print(string)
    return None

def main2(content,cled=None):
    templist = []
    global time_prefix
    define = ''
    conten = []
    chara_pos = {}  # 当前在场角色的字典，{角色:[位置，立绘名字]}
    c = content.split('\n')
    conc = len(c)
    iz = 0
    continue_flag = 0
    last_sid = ''
    actiontemp = ''
    text_flag = 0
    bg_flag = 0
    face_flag = 0
    shakeflag = 0
    while iz < conc:
        #print(iz)
        d = translator(c[iz],text_flag,bg_flag,face_flag,shakeflag)
        if d == None:
            iz += 1
            continue
        if d[0] == 0:
            conten.append('    ' + d[1])
        elif d[0] == 1:
            conten.append('    ' + d[2])
            if d[1] not in define:
                define += '' + d[1]
        elif d[0] == 2:
            if d[1] not in define:
                define += d[1]
            conten.append(d[3])
            next_delface = d[2]
        elif d[0] == 3:
            try:  # 原脚本重复del，会报错
                conten.append('    ' + d[1] + next_delface + '\n')
                del next_delface
            except:
                pass
        elif d[0] == 4:
            name = '%s_%s_%s' % (d[2][0], d[2][1], d[2][2])
            if d[1] not in define:
                define += '' + d[1]
            if d[3][1] not in chara_pos:
                conten.append('    ' + chara_print % (d[2][1], name, 0))
                conten.append('    ' + 'with dissolve\n')
                chara_pos.update({d[3][1]: [0, name]})
            else:
                now_pos = chara_pos[d[3][1]][0]
                chara_pos.update({d[3][1]: [now_pos, name]})
                conten.append('    ' + chara_print % (d[2][1], name, pos_converter(now_pos)))
        elif d[0] == 5:
            try:
                conten.append('    ' + d[1] % (d[2] + ' ' + chara_pos[d[2]][1]))
                conten.append('    ' + 'with dissolve\n')
                del chara_pos[d[2]]
            except:
                pass
        elif d[0] == 6:
            conten.append(chara_print % (d[1], chara_pos[d[1]][1], pos_converter(d[2])))
            conten.append('    ' + 'with move\n')
            chara_pos.update({d[1]: [d[2], chara_pos[d[1]][1]]})
        elif d[0] == 7:
            name = '%s_%s_%s' % (d[1][0], d[1][1], d[1][2])
            if name not in define:
                define += chara_template.format(name, d[1][1],getcharaypos(d[1][1], d[1][2]))
            posx = d[1][4]
            conten.append(chara_print % (d[1][1], name, pos_converter(d[1][4])))
            conten.append('    ' + 'with dissolve\n')
            if 'with dissolve' in conten [-3] and 'scene' not in conten[-3]:
                del conten [-3]
            chara_pos.update({d[1][1]: [pos_converter(d[1][4]), name]})
        elif d[0] == 8:
            if chara_pos != {}:
                for i in chara_pos:
                    charater = chara_pos[i][1]
                    conten.append('    hide %s %s\n' % (i, charater))
                conten.append('    ' + 'with dissolve\n')
        elif d[0] == 13:
            time_prefix = int(d[3])
            conten.append('    ' + d[2])
            try:
                d[4]
            except:
                if d[1] not in define:
                    define += '' + d[1]
            conten.append('with  Dissolve({0}) \n    $camera_reset()\n'.format(float(int(d[3]) / 100)))
            time_prefix = float(int(d[3]) / 100)
        elif d[0] == 14:
            sound_dur = round(
                librosa.get_duration(filename='D:\\newrenpywork\\majo_koi\\game\\sound\\%s.ogg' % last_sid), 4)
            conten.append('    pause %s\n' % sound_dur)
        elif d[0] == 15:
            conten.append('    ' + d[1])
            last_sid = d[2]
        elif d[0] == 16:
            conten = conten[:-1]
            conten .append( '    $renpy.music.play(\'sound/{0}.ogg\',\'loopback_sound\')\n'.format(last_sid))
        elif d[0] == 18:
            if d[1] == '18':
                actiontemp = '    $ text_transform = shake'
                text_flag = 1
            elif d[1] == '34':
                actiontemp = '    $ text_transform = id_34'
                text_flag = 1
        elif d[0] == 19:
            if conten[-1].startswith('    "')and not conten[-1].endswith('\n'):
                conten.insert(-1,actiontemp+'\n')
            else:
                conten.append(actiontemp+'\n')
            conten.append('    "%s" \n    $ text_transform = NullTransform\n'%(d[1]))
            text_flag = 0
            actiontemp =''
        elif d[0] == 20:
            if d[1][0] == '14':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_14\n')
            elif d[1][0] =='3':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_3\n')
            elif d[1][0] =='13':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_13\n')
            elif d[1][0] =='36':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_36\n')
            elif d[1][0] =='42':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_14\n')
            elif d[1][0] == '16':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_16\n')
            elif d[1][0] == '9':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_9\n')
            elif d[1][0] == '10':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_10\n')
            elif d[1][0] == '4':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_4\n')
            elif d[1][0] == '11':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_11\n')
            elif d[1][0] == '24':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_24\n')
            elif d[1][0] == '8':
                conten.append(chara_print % (d[1][1], chara_pos[d[1][1]][1], pos_converter(chara_pos[d[1][1]][0])))
                conten.append('        ' + 'id_16\n')
            else:
                pass
                # templist.append(d[1][0])
        elif d[0] == 21:
            if d[1] == '1':
                bg_flag = 1
            if d[1] == '0':
                bg_flag = 0
        elif d[0] == 22:
            try:
                actionimg = next_delface
                face_flag = 1
                if d[1] =='42':

                        conten.append('    $ sidetransform = id_14\n')
                        conten.append('    show side %s\n'%actionimg)
                elif d[1] == '9':
                    conten.append('    $ sidetransform = id_9\n')
                    conten.append('    show side %s\n' % actionimg)

            except:
                pass
        elif d[0] ==23:
            conten.append('    "%s" \n    $ sidetransform = NullTransform\n'%(d[1]))
            face_flag = 0
        elif d[0] ==24:
            conten.append('    scene transparent onlayer blackout\n')
        elif d[0] ==25:
            conten.append(d[1])
        elif d[0] == 26:
            shakeflag = 1
        elif d[0] == 27:
            shakeflag = 0
        if continue_flag == 0:
            iz += 1
    if define[-4:] == '    ':
        define = define[:-4]
    newcontemp = ''
    templist.sort()
    print(list(set(templist)))
    if cled !=  None:
        conten += cled
    for i in conten:
        newcontemp += i
    return define, newcontemp.split('\n')
