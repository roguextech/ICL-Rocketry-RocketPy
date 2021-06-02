
''' 
ICLR ROCKETPY - MISSION ANALYSER

- User describes high level requirements
- Program sets and enforces bounds based on mission objectives

There are several "Rocket Focus" targets which pre-populate the output vector
E.g. Payload --> Mass, Dimensions, Flight objective, Class
     Staging --> Number of Stages, Flight objective, Class


Output Vector: by default null; 
'''

import pickle                   # For serialise/deserialise
import Rocket                   # Rocket class
import helper_functions
import physics_constraints

# Functions
def load(name, path="./rockets/"):
    return(pickle.load(open(path+name+".pickle", "rb")))


# List of all design constraints - remember these are ranges, not necessarily exact values
constraints = [ ["apogee", "flight_time", "max_velocity"],                                              # Flight Constraints
                ["radial_drift", "safety_factor", "ground_hit_velocity"],                               # Safety Constraints
                ["class", "cost"],                                                                      # Team Limitations
                ["payload_mass", "payload_volume"],                                                     # Payload Characteristics
                ["num_stages"],                                                                         # Staging Requirements
                ["num_motors", "isp", "burn_time", "thrust_limits"]                                     # Engine Characteristics
              ]

constraints_flat = helper_functions.flat_2d_array(constraints)

rocket_objectives = {"Payload": [1,3], "Staging": [1,4], "Novel Propulsion": [1,5], "Custom": []}       # Top level objectives

defined_constraints = {}

# Select new or existing rocket design
while True:

    opt = int(input("Select 1 to create a new rocket, 2 to load an existing design: "))

    if opt == 1:
        name = input("\nEnter the name of your new rocket: ")
        print("")
        [print(f"{i}. {n}") for i,n in enumerate(rocket_objectives)]
        objectives_opt = int(input("Select your rocket objective: "))

        # Highlights mandatory fields
        enforced_constraints = [constraints[i] for i in rocket_objectives[list(rocket_objectives)[objectives_opt]]]
        enforced_constraints = helper_functions.flat_2d_array(enforced_constraints)
        break
        
    elif opt == 2:
        name = input("\nEnter the name of your rocket: ")
        rocket = load(name)

        # Retrieving data from Rocket object
        enforced_constraints = rocket.enf_const
        defined_constraints = rocket.constraints

        break
        
    
while True:

    print("")
    count = 0                                                                                           
    for const in constraints_flat:
        if const in enforced_constraints:
            try: print(f"{count}. (REQUIRED) {const}: {defined_constraints[const]}")                    
            except: print(f"{count}. (REQUIRED) {const}")
        else: 
            try: print(f"{count}. {const}: {defined_constraints[const]}")
            except: print(f"{count}. {const}")
        count +=1

    user_const = input("\nUsing SI units, set a constraint (idx lower_bound upper_bound) or type \"done\" to end the script: ")
    
    if (user_const.lower()) == "done":
        
        if all(const in defined_constraints for const in enforced_constraints):
            rocket = Rocket.Rocket(name, defined_constraints, enforced_constraints)
            rocket.save()
            break

        else:
            print("\nPlease define all required constraints before saving\n")
            continue

    user_const = user_const.split()

    try:
        if (float(user_const[1]) > float(user_const[2]) or float(user_const[1]) < 0 or float(user_const[2]) < 0):
            print("\nMake sure the lower bound is smaller than the upper bound and that both values are +ve.")
            continue
    except:
        print("\nThere was an unexpected input. Try again")
        continue

    defined_constraints[constraints_flat[int(user_const[0])]] = [float(user_const[1]), float(user_const[2])]


# Evaluate design envelopes 
# Very basic, idea is that Systems expands this!

rocket = physics_constraints.calculate_physics_constraints(rocket)

print("\nDefined rocket constraints:")
print(rocket.show_constraints())