package tech.sda.iqa.nqs;



import static spark.Spark.*;
import spark.Route;
import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.util.annotation.QueryAnnotaion;

public class NQS_server {

	private static QueryBuilder qb = new QueryBuilder();
	
	static String getNQS(String ques){
		//qb = new QueryBuilder();
		qb.setQuery(ques);
		qb.buildQuery();
		String nqs = qb.getCharacterizedString();
//		nertags = ner_resolver.nertag;
		return nqs;
	}
	
	public static void main(String[] args) {
		port(4568);
		
        post("/question", (req, res) -> {
        	String question_nqs = getNQS(req.queryParams("question"));
        	return question_nqs;        	
        });
        
        post("/entity_spotting",(req,res) -> {
        	String nqs = req.queryParams("nqs");
        	String question = req.queryParams("question");
        	Nqs q1 = new Nqs(question,nqs,"","");
        	QueryAnnotaion.annotate(q1);
        	System.out.println(q1.predicateCandidate);
        	return q1.predicateCandidate;
        });
    }
	
	
}
