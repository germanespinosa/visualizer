params='-w 100 -p 80 -n "work done 80" -t "in work"'

work = 30; progress = 10; size = 30; columns = 70; progress_string = '%d/%d' % (progress, work); progress = int(progress / work * size); notes = 'processing world_5_3...'; gauge = '|'+'='*progress+'>'+'-'*(size-progress)+'| '+progress_string+' ' + notes; print(gauge[0:columns] if len(gauge) > columns else gauge + ' ' * (columns - len(gauge)), end='')
