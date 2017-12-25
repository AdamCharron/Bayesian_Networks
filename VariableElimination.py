from BayesianNetwork import *

'''
multiply_factors(factors)

Parameters :
              factors : a list of factors to multiply
Return:
              a new factor that is the product of the factors in "factors"
'''

def multiply_factors(factors):

    # Create new factor with scope of all the variables together
    newScope = []
    name = "Product of: ["
    for i in range(len(factors)):
        name += factors[i].name + ","
        for var in factors[i].get_scope():
            if var not in newScope:
                newScope.append(var)
    name += "]"
    newFactor = Factor(name, newScope)

    # Create list, with one element per factor (ordered), where each element is
    # a list of indices mapping factor's var indices to newFactor's var indices
    # Ex: newScope = [A,B,C,D,E...], f(D,B) is 2nd factor in factors
    #     -> factorList[1] = [3,1]
    #     Thus, we know factorList[1][0] refers to D variable
    factorList = [0]*len(factors)
    for i in range(len(factors)):
        tempList = []
        for j in range(len(factors[i].get_scope())):
            for k in range(len(newScope)):
                if newScope[k] == factors[i].get_scope()[j]:
                    tempList.append(k)
        factorList[i] = tempList
    
    newValList = []
    for iterator in newFactor.get_assignment_iterator():
        p = 1
        for i in range(len(factors)):
            tempList = list(iterator)
            paramList = []
            for j in factorList[i]:
                paramList.append(tempList[j])
            p *= factors[i].get_value(paramList)
        tempList.append(p)
        newValList.append(tempList)

    newFactor.add_values(newValList)
    return newFactor





'''
restrict_factor(factor, variable, value):

Parameters :
              factor : the factor to restrict
              variable : the variable to restrict "factor" on
              value : the value to restrict to
Return:
              A new factor that is the restriction of "factor" by
              "variable"="value"
      
              If "factor" has only one variable its restriction yields a 
              constant factor
'''
def restrict_factor(factor, variable, value):

    if factor.get_scope() == []:
        return factor

    # Create new scope without restricted variable for new factor
    newScope = []
    for i in factor.get_scope():
        if i != variable:
            newScope.append(i)
    newFactor = Factor("restrictedFactor", newScope)
        

    # Find the index value of the variable for lookup in value list
    for var in range(len(factor.get_scope())):
        if factor.get_scope()[var] == variable:
            index = var

    # For each assignment permutation that has this parameter value,
    # remove the value, add on the probability, and append to a valueList to be
    # passed to the new factor via add_values
    newValueList = []
    iterator = factor.get_assignment_iterator()
    for permu in iterator:
        if permu[index] == value:
            permu.append(factor.get_value(permu))
            permu.pop(index)
            newValueList.append(permu)
    if newValueList == []:
        newFactor.add_value_at_assignment(value, [])
    else:
        newFactor.add_values(newValueList)
    return newFactor





'''    
sum_out_variable(factor, variable)

Parameters :
              factor : the factor to sum out "variable" on
              variable : the variable to sum out
Return:
              A new factor that is "factor" summed out over "variable"
'''
def sum_out_variable(factor, variable):

    if factor.get_scope() == []:
        return factor

    # Create new scope without restricted variable for new factor
    newScope = []
    for i in factor.get_scope():
        if i != variable:
            newScope.append(i)
    newFactor = Factor("summedFactor", newScope)

    # Find the index value of the variable for lookup in value list
    index = -1
    for var in range(len(factor.get_scope())):
        if factor.scope[var] == variable:
            index = var
    # If the variable is not in the factor
    if index == -1:
        return factor

    # Go through each permutation and wherever all variables, except the one
    # being summed over, are the same, sum the probabilities
    newValueList = []
    iterator = factor.get_assignment_iterator()
    iteratorList = []
    for permu in iterator:
        test = list(permu)
        p_sum = 0
        for val in factor.get_scope()[index].domain():
            test[index] = val
            p_sum += factor.get_value(test)
        test.pop(index)
        test.append(p_sum)
        newValueList.append(test)

    #print(newValueList)
    if newValueList == []:
        newFactor.add_value_at_assignment([factor.get_value([])], [])
    else:
        newFactor.add_values(newValueList)
    return newFactor


    
'''
VariableElimination(net, queryVar, evidenceVars)

 Parameters :
              net: a BayesianNetwork object
              queryVar: a Variable object
                        (the variable whose distribution we want to compute)
              evidenceVars: a list of Variable objects.
                            Each of these variables should have evidence set
                            to a particular value from its domain using
                            the set_evidence function. 

 Return:
         A distribution over the values of QueryVar
 Format:  A list of numbers, one for each value in QueryVar's Domain
         -The distribution should be normalized.
         -The i'th number is the probability that QueryVar is equal to its
          i'th value given the setting of the evidence
 Example:

 QueryVar = A with Dom[A] = ['a', 'b', 'c'], EvidenceVars = [B, C]
 prior function calls: B.set_evidence(1) and C.set_evidence('c')

 VE returns:  a list of three numbers. E.g. [0.5, 0.24, 0.26]

 These numbers would mean that Pr(A='a'|B=1, C='c') = 0.5
                               Pr(A='a'|B=1, C='c') = 0.24
                               Pr(A='a'|B=1, C='c') = 0.26
'''
def VariableElimination(net, queryVar, evidenceVars):

    factorList = list(net.factors())
    
    # Restrict the variables whose evidences have been set
    for var in evidenceVars:
        for i in range(len(factorList)):
            if var in factorList[i].get_scope():
                factorList[i] = restrict_factor(factorList[i], var, var.get_evidence())        
    
    # Sum out all unneeded variables to get a factor only of queryVar
    orderedScope = min_fill_ordering(factorList, queryVar)
    for var in orderedScope:
        tempList = []
        for factor in factorList:
            if factor.get_scope == []:
                factorList.remove(factor)
                continue
            if var in factor.get_scope():
                tempList.append(factor)
        summedFactor = sum_out_variable(multiply_factors(tempList), var)
        for factor in tempList:
            if factor in factorList:
                factorList.remove(factor)
        factorList.append(summedFactor)

    # Multiply all factors together to get one factor
    finalFactor = multiply_factors(factorList)

    # Make and return a list testing all assignable values in this final factor
    returnList = []
    for val in finalFactor.get_scope()[0].domain():
        returnList.append(finalFactor.get_value([val]))

    sum_i = 0
    for i in returnList:
        sum_i += i
    for i in range(len(returnList)):
        returnList[i] *= 1/sum_i
    return returnList
