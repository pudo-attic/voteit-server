from bson.code import Code

from voteit.core import votes

REDUCE = Code("""
function(obj, prev) {
    if (!prev.votes.hasOwnProperty(obj.option)) {
        prev.votes[obj.option] = 1;
    } else {
        prev.votes[obj.option]++;
    }
    //prev.count++;
};
""")


def generate_stances(blocs=[], filters={}):
    data = votes.group(blocs, filters, {"votes": {}}, REDUCE)
    print data
    return data
