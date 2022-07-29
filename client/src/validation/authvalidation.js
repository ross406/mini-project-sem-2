import isEmpty from "./is-empty";

export const registerValidation = (user) => {
    let errors = {}
    if((isEmpty(user.name)) || (isEmpty(user.email)) || (isEmpty(user.password)) || (isEmpty(user.password2))) {
        if((isEmpty(user.name))) errors.name = "Name is required!"
        if((isEmpty(user.email))) errors.email = "Email is required!"
        if((isEmpty(user.password))) errors.password = "password is required!"
        if((isEmpty(user.password2))) errors.password2 = "confirm password is required!"

        return errors;
    }

    if(user.password.length < 8){
        errors.common = "Password should be more than 8 charecters!"
    }
    if(user.password !== user.password2){
        errors.common = "Password and confirm password should match!"
    }

    return errors;
};
  
export const loginValidation = (user) => {
    let errors = {}
    if((isEmpty(user.email)) || (isEmpty(user.password))) {
        if((isEmpty(user.email))) errors.email = "Email is required!"
        if((isEmpty(user.password))) errors.password = "password is required!"
        return errors;
    }
    return errors;
};
  