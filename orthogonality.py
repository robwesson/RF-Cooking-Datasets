def calcOrthogonality(V1,V2):
    # takes two vectors of the same length and cacluates their orthogonality
    # as dot product over product of magnitudes (Cosine Similarity Function)
    # V1 = a1x + b1y + c1z
    # V2 = a2x + b2y + c2z
    # V1.V1 = a1*a2 + b2*b2 + c1*c2 + ...
    # then divide dot product by magV1.MagV2
    len1 = len(V1)
    len2 = len(V2)
    
    # check for equal vector length
    if not (len1 == len2):
        print('Vectors for Orthogonality do not have equal length')
        print('V1 has len ' +str(len1))
        print('V2 has len ' + str(len2))
        return(None)
    else:
        magV1=0
        magV2=0
        dotProduct=0
        for i in range (0,len1):
            dotProduct+= V1[i]*V2[i]
            magV1+=V1[i]**2
            magV2+=V2[i]**2
        
        # need to sqrt the sum-of-squares to get each vector's magnitude
        magV1 = magV1**0.5
        magV2 = magV2**0.5
        
        return(dotProduct/(magV1*magV2))
        
# self test code
# uncomment and run this python file standalone to test
#V1 = [1,0,1]
#V2 = [0,1,1]
#result = calcOrthogonality(V1,V2)
#print(result)
