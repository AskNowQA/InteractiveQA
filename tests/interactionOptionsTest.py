from common.interaction.interactionOptions import InteractionOptions
from common.interaction.interactionOption import InteractionOption

if __name__ == "__main__":
    ios = InteractionOptions([], None, None)

    q1 = {'name': 'cq1', 'complete_confidence': 0.2, 'removed': False}
    q2 = {'name': 'cq2', 'complete_confidence': 0.5, 'removed': False}
    q3 = {'name': 'cq3', 'complete_confidence': 0.7, 'removed': False}
    io1 = InteractionOption("o1", "q1", [q1, q2])
    io2 = InteractionOption("o2", "q2", [q1, q3])
    io3 = InteractionOption("o3", "q3", [q2, q3])
    ios.all_queries.extend([q1, q2, q3])
    ios.all_ios.extend([io1, io2, io3])

    while ios.has_interaction():
        io = ios.interaction_with_max_information_gain()
        print "max information gain:" + str(io)
        io = ios.interaction_with_max_probability()
        print "max probability:" + str(io)
        io = ios.interaction_with_max_option_gain(.1)
        print "max option gain:" + str(io)
        print io
        ios.update(io, True)

    print "Done!"
