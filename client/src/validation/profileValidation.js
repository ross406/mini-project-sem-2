import isEmpty from "./is-empty";

  
export const createProfileValidation = (profileData) => {
    let errors = {}
    if((isEmpty(profileData.handle)) || (isEmpty(profileData.skills)) || (isEmpty(profileData.status))) {
        if((isEmpty(profileData.handle))) errors.handle = "Handle is required!"
        if((isEmpty(profileData.skills))) errors.skills = "Skills is required!"
        if((isEmpty(profileData.status))) errors.status = "Status is required!"
        return errors;
    }
    return errors;
};

export const addExperienceValidation = (expData) => {
    let errors = {}
    if((isEmpty(expData.company)) || (isEmpty(expData.title)) || (isEmpty(expData.from)) || (isEmpty(expData.to))) {
        if((isEmpty(expData.company))) errors.company = "Company is required!"
        if((isEmpty(expData.title))) errors.title = "Title is required!"
        if((isEmpty(expData.from))) errors.from = "From date is required!"
        if(!expData.current) {
            if((isEmpty(expData.to))) errors.to = "To date is required!"
        }
        return errors;
    }
    return errors;
};

export const addEducationValidation = (eduData) => {
    let errors = {}
    if((isEmpty(eduData.school)) || (isEmpty(eduData.degree)) || (isEmpty(eduData.fieldofstudy)) || (isEmpty(eduData.from)) || (isEmpty(eduData.to))) {
        if((isEmpty(eduData.school))) errors.school = "School is required!"
        if((isEmpty(eduData.degree))) errors.degree = "Degree is required!"
        if((isEmpty(eduData.fieldofstudy))) errors.fieldofstudy = "Field Of Study is required!"
        if((isEmpty(eduData.from))) errors.from = "From date is required!"
        if(!eduData.current) {
            if((isEmpty(eduData.to))) errors.to = "To date is required!"
        }       
        return errors;
    }
    return errors;
};