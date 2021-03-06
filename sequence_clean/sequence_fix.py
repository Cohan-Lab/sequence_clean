import closest_rel
import random
import time
import datetime
import os


##T5c10 has underscore, have to specify some params in closest_rel so things
##like that are accepted..

def import_fasta(filename):
    f = open(filename, 'r')
    f2= f.readlines()
    return f2

def read_fasta(fasta_list):
    dct = {}
    index = 0
    
    for line in fasta_list:
        if line[0] == '>':
            #add line as a string as key #1**
            dct[line[1:].strip()] = fasta_list[index + 1].strip()
        index += 1
    return dct

def percent_gap(dct,index):
    """calculates percentage of strains that also have a gap at the same index
    DO I COUNT THE STRAIN WE'RE LOOKING AT?"""
    # start = time.time()
    num_strains = len(dct)
    gaps = 0
    for s in dct:
        #try statement to catch the cases at the ends of seqs where 
        #some seqs will have gaps and other won't have anything
        try:
            if dct[s][index] == "-":
                gaps += 1

        #COUNTING HAVING NO NUCLEOTIDE AS A GAP
        except IndexError: 
            gaps += 1

    # print "%/ gap took ",time.time()-start
    return float(gaps)/num_strains

def remove_column(dct,index):
    """Removes the nucleotide at the given index for
        all sequences"""
    # start = time.time()
    ## COULD OPTIMIZE BY MAYBE NOT REJOINING? KEEP LISTS UNTIL END? 
    # print "DOING NEW"
    for s in dct:
        seq = list(dct[s])
        try:
            seq.pop(index)
        except:
            # print "PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSING"
            pass
        dct[s] = "".join(seq)
    # print "Remove column took", time.time()-start
    return dct

def weighted_seq_choose(strain_dct,strain_node,rels,index,level=0):
    ##LEVEL is how many upward requests have been requested. Idea is that you
    ##store each level of ancestors and only get more if levels > len(rels)
    ##This is to avoid the problem of using all the levels for each replacement
    ##since that sacrifices closeness and makes some of the replacements less acceptable

    start = time.time()
    nucs = {}
    for r in rels[level]:
        try:
            nucleotide = strain_dct[r[0]][index]
            if nucleotide in nucs:
                nucs[nucleotide] += 1
            else:
                nucs[nucleotide] = 1
        except:
            pass

    pop = []
    for z in nucs:
        if z in ["A","T","G","C"]:
            for i in range(nucs[z]):
                pop.append(z)
    if not pop:
        ##Have to get the parent of the parent of the strain
        ##HOW MANY TIMES SHOULD THIS BE REPEATED??
        ##MAKE SURE THIS IS ACTUALLY WORKING/GOING UP THE TREE MORE THAN ONCE
        try:
            rels_next = rels[level+1]
            parent2 = closest_rel.get_parent(strain_node)
        except:
            rels_next,parent2 = closest_rel.get_parents_parent_relatives(strain_node)  
            rels.append(rels_next)
        return weighted_seq_choose(strain_dct,parent2,rels,index,level+1)

    choice = random.choice(pop)
    return choice,rels

def replacer(newick_file,dct,cutoff):
    tree = closest_rel.tree_from_string(newick_file)
    orig_dct = dct.copy()
    bad_list = []
    s_num = 0
    c_removals = 0
    g_replacements = 0
    base_replacements = 0
    print orig_dct.keys()
    
    for strain in dct.keys():
        index = 0
        rels = [closest_rel.closest_relative(tree,strain)]
        if type(rels[0]) == tuple:
            #for case of just one relative
            a = [[]]
            a[0].append(rels[0])
            rels = a
        sequence_copy = str(dct[strain])
        strain_node = ""
        for nuc in sequence_copy:
            if nuc == '-':
                p_gaps = percent_gap(dct,index)
                if p_gaps <=  cutoff:
                    if strain_node == "":
                        strain_node = closest_rel.strain_to_node(tree,strain)

                    closest,rels = weighted_seq_choose(orig_dct,strain_node,rels,index)
                    ###Could optimize this bit here, save closest relatives and just do op once, index later
                    ###BUT now have to create a hierarchy of rel levels so that each replacement will
                    ###only jump up IF necessary, since otherwise you sacrifice closeness.
                    if closest:
                        old_seq = list(dct[strain])
                        old_seq[index] = closest
                        dct[strain] = "".join(old_seq)
                        g_replacements += 1
                    else:
                        print "FOUND NO CLOSEST RELATIVE EVER...?"
                    index += 1
                else:
                    dct = remove_column(dct,index)
                    orig_dct = remove_column(orig_dct,index)
                    c_removals += 1
            elif nuc not in ["A","T","G","C"]:
                strain_node = closest_rel.strain_to_node(tree,strain)
                closest,rels = weighted_seq_choose(orig_dct,strain_node,rels,index)
                if closest:
                    old_seq = list(dct[strain])
                    old_seq[index] = closest
                    dct[strain] = "".join(old_seq)
                    base_replacements += 1
                index += 1  
            else:
                index += 1  
        s_num += 1

    log = {'Strains analyzed':str(dct.keys()),
            'Cutoff percentage':str(cutoff),
           'Number of strains in Newick Tree':str(len(dct.keys())),
           'Number of column removals':str(c_removals),
           'Number of gap replacements':str(g_replacements),
           'Number of irregular base replacements':str(base_replacements)}
    return dct,log

def fasta_to_file(dct,fasta_out):
    new_fasta = ''
    for k in dct:
        new_fasta += '>' + k + '\n'
        new_fasta += dct[k] + '\n'
    f_out = open(fasta_out, 'w')
    f_out.write(new_fasta)
    f_out.close()

def logging(logs,log_name):
    #logs is a dictionary of all items to be logged
    string = "Date: " + str(datetime.datetime.today())+"\n"+"\n"
    for k in logs:
        string += k+": "+logs[k]+'\n'+'\n'
    f_out = open(log_name,'w')
    f_out.write(string)
    f_out.close()

def import_settings():
    """Imports settings from file. Expects a newick file, a fasta file, 
        a name for the new fasta file, and a name for the log file
    THE SETTINGS FILE MUST BE CALLED 'seq_clean_settings.txt' and must be in 
    the current directory! If not found, will write to log file that it can't find
    settings in CWD.
        """
    try:
        f_in = open('seq_clean_settings.txt','r')
        lines = f_in.readlines()
        newick_file = lines[0]
        fasta_file = lines[1]
        cutoff = lines[2]
        fasta_out = lines[3]
        log_name = lines[4]
        settings = [newick_file,fasta_file,cutoff,fasta_out,log_name]
        settings = [i.strip() for i in settings]
        settings[2] = float(settings[2])
        return settings
    except:
        return False

def main():
    """
    newick_file: name of newick file corrosponding to the fasta file
    fasta_file: fasta file to analyze
    cutoff: percentage (i.e. .1 = 10%) under which closest relative replacement will occur. 
        if above, remove the column.
    fasta_out: name for the new fasta file with a .fas at the end
    log_name: name for the log file with a .txt at the end
    """
    settings = import_settings()
    print settings
    if settings:
        try:
            newick_file,fasta_file,cutoff,fasta_out,log_name = settings
        except:
            logging({"Error":"Could not find all required settings in 'seq_clean_settings.txt' in "+os.getcwd()},
                "-- NEED: newick file, fasta file, cutoff, new fasta file name, new log name. Each should be entered on a new line in the specified order",
                "SEQ_CLEAN_ERROR_LOG.txt")
            return
    else:
        logging({"Error":"Could not find file 'seq_clean_settings.txt' in "+os.getcwd()},"SEQ_CLEAN_ERROR_LOG.txt")
        return
    start = time.time()
    fasta_string = import_fasta(fasta_file)
    fasta_dict = read_fasta(fasta_string)
    fasta_dict_copy = fasta_dict.copy()
    print newick_file,type(cutoff)
    new_fasta_dict,logs = replacer(newick_file,fasta_dict_copy,cutoff)
    elapsed = time.time()-start
    fasta_to_file(new_fasta_dict,fasta_out)
    logs['Run time'] = str(elapsed)+" seconds"
    logs['Number of strains in fasta file'] = str(len(fasta_dict))
    logging(logs,log_name)


main()

# cutoffs = [.1]

# def cutoff_trials(fasta_file,newick_file,cutoffs):
#     ite = 0
#     for t in cutoffs:
#         print "running with cutoff",t
#         filename = str(cutoffs[ite]) + " clean_cut_test.fas"
#         start = time.time()
#         fasta_string = import_fasta(fasta_file)
#         fasta_dict = read_fasta(fasta_string)
#         fasta_dict_copy = fasta_dict.copy()
#         new_fasta_dict,logs = replacer(newick_file,fasta_dict_copy,t)
#         elapsed = time.time()-start
#         fasta_to_file(new_fasta_dict,filename)
#         logs['Run time'] = str(elapsed)+" seconds"
#         logs['Number of strains in fasta file'] = str(len(fasta_dict))
#         logging(logs,str(cutoffs[ite]) + " LOG")
#         ite+=1


# cutoff_trials('23 Oct with outgroup (fromAligned 31Aug).fas','MLtree from23 Oct with outgroup (fromAligned 31Aug).nwk',cutoffs)
