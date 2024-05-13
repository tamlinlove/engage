Header header
# the user id 
int16 id
# the group to whom a person belong
int8 group
# number of people in the scene
int8 num_people
# whether they are over 18
bool is_minor
# image to show
sensor_msgs/CompressedImage image  
# blank image to show
sensor_msgs/CompressedImage blank_image  
# text on the explanation page
string explanation
string counterfactual
# text on the prediction page
string question_context
string question_text
# possible answers
string[] answer_list_gaze
string[] answer_list_uncertainty
# index of the correct answer
int8 correct_answer_gaze
int8 correct_answer_uncertainty
# index of the user answer
int8 user_answer_gaze
int8 user_answer_uncertainty
