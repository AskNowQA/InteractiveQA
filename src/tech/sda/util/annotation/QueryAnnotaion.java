package tech.sda.util.annotation;

import java.util.HashSet;
import java.util.Set;

import tech.sda.interactiveqa.Nqs;

public class QueryAnnotaion {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		testrelanno();
	}
	public static void annotate(Nqs n){
		
		//HashSet<String> rel = new HashSet<String>();
		//rel.add(n.getDesire());
		//rel.add(n.getRelation2());
		//n.resourceSpotlight = EntityAnnotation.getEntityAnnotation(n.nlQuery);
		//n.resourceFOX = EntityAnnotation.getFOXAnnotation(n.nlQuery);
		//if (n.resourceSpotlight!=null)
		n.predicateCandidate = PredicateAnnotation.getPredicateAnnotation(n);
		//else
		//	n.predicateCandidate=null;	
			
		//System.out.println("Res: "+n.Resource);
		//for (String r : n.Resource){
	//		n.Predicate =RelationAnnotation.getRelAnnotation(rel, r);
		//}
	}
	
	static void testrelanno(){
		//Test: RelationAnnotaion
		//<Ques>In which country does the Ganges start?</Ques>
		//<NQS>[WH] = which, [R1] = does, [D] =  country, [R2] = start In, [I] = the  Ganges</NQS>
				HashSet<String> rel = new HashSet<String>();
				rel.add("country");
				rel.add("start");
				String entity = "<http://dbpedia.org/resource/Ganges>";
				//System.out.println(RelationAnnotation.getRelAnnotation(rel, entity));
	}
}
