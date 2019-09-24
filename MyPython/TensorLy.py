import tensorly as tl
import numpy as np
from tensorly.decomposition import tucker, parafac, non_negative_tucker

gene_matrix=np.loadtxt("LAML_DNMT3A_mRNA.txt", delimiter='\t', usecols=range(1,17), skiprows=1)
methyl_matrix=np.loadtxt("LAML_DNMT3A_methylation.txt", delimiter='\t', usecols=range(1,17), skiprows=1)
miRNA_matrix=np.loadtxt("LAML_DNMT3A_miRNA_v4.txt", delimiter='\t', usecols=range(1,17), skiprows=1)

data=np.ndarray((3,8062,16))
data[0,:,:]=gene_matrix
data[1,:,:]=methyl_matrix
data[2,:,:]=miRNA_matrix

#out=parafac(data, rank=2,init='random')
#np.savetxt("rank2out.txt",out)

for i in range(2,17):
	lst_out=parafac(data, rank=i, init='random')
	for j, out in enumerate(lst_out):
		np.savetxt("3out_"+str(i)+"."+str(j+1)+".txt", out, fmt='%.5f', delimiter='\t')
	#f=open("TDout_rank"+str(i)+".txt2", 'w')
	#print len(out)
	#print out[0].shape
	#f.write=(out)
	#f.close()
	
	#np.savetxt("out_"+str(i)+".txt",out)
