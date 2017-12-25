from MedicalBayesianNetwork import *
from VariableElimination import *

'''
Parameters:
             medicalNet - A MedicalBayesianNetwork object                        

             patient    - A Patient object
                          The patient to calculate treatment-outcome
                          probabilites for
Return:
         -A factor object

         This factor should be a probability table relating all possible
         Treatments to all possible outcomes
'''
def DecisionSupport(medicalNet, patient):
    
    factorList = list(medicalNet.net.factors())

    # Set evidence for all patient evidence values
    medicalNet.set_evidence_by_patient(patient)
    evidenceVars = patient.evidenceVariables()
    evidenceVals = patient.evidenceValues()

    # Restrict the variables whose evidences have been set
    for var in evidenceVars:
        for i in range(len(factorList)):
            if var in factorList[i].get_scope():
                factorList[i] = restrict_factor(factorList[i], var, var.get_evidence())
    
    # Multiply all factors together to get one factor
    productFactor = multiply_factors(factorList)
    
    # Make a new factor which is the productFactor normalized
    iterator = productFactor.get_assignment_iterator()
    total = 0
    valList = []
    for permu in iterator:
        permuList = list(permu)
        total += productFactor.get_value(permuList)
    for permu in iterator:
        tempList = list(permu)
        tempList.append(productFactor.get_value(tempList)/total)
        valList.append(tempList)

    newproductFactor = Factor(productFactor.name, productFactor.scope)
    newproductFactor.add_values(valList)

    Tvars = list(medicalNet.getTreatmentVars())
    Ovars = list(medicalNet.getOutcomeVars())

    # Find P(...Ti) factor with all Treatment vars
    # Find P(...Ti, ...Oj) factor with all Treatment and Outcome vars
    Ofactors = newproductFactor
    Tfactors = newproductFactor
    for var in newproductFactor.get_scope():
        if var not in Tvars: 
            Tfactors = sum_out_variable(Tfactors, var)
            if var not in Ovars:
                Ofactors = sum_out_variable(Ofactors, var)

    finalFactor = Factor("finalFactor", Ofactors.get_scope())

    # Map indices of vars in Tvars to OVars
    Tindices = [0]*len(Tfactors.get_scope())
    for i in range(len(Ofactors.get_scope())):
        for j in range(len(Tvars)):
            if Ofactors.get_scope()[i] == Tfactors.get_scope()[j]:
                Tindices[j] = i
                break            

    # Compute conditional probabilities
    newValList = []
    Oiterator = Ofactors.get_assignment_iterator()
    Titerator = Tfactors.get_assignment_iterator()
    for Opermu in Oiterator:
        tempList = []
        OpermList = list(Opermu)
        for Tpermu in Titerator:
            flag = True
            TpermList = list(Tpermu)
            for i in range(len(TpermList)):
                if TpermList[i] != OpermList[Tindices[i]]:
                    flag = False
            if not flag:
                continue
            if Tfactors.get_value(TpermList) == 0:
                p = 0
            else:
                p = Ofactors.get_value(OpermList)/Tfactors.get_value(TpermList)
        tempList = OpermList
        tempList.append(p)
        newValList.append(tempList)

    finalFactor.add_values(newValList)
    return finalFactor
