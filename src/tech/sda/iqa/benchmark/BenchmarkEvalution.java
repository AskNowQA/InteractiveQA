package tech.sda.iqa.benchmark;

import java.util.List;

import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.interactiveqa.Parser;
import tech.sda.iqa.nqs.QueryBuilder;
import tech.sda.iqa.util.TempalateGeneratorServer;
import tech.sda.iqa.util.annotation.QueryAnnotaion;

public class BenchmarkEvalution {
	private static QueryBuilder qb = new QueryBuilder();
	public static void main(String[] args){ 
		//testQALD();
		testSingle();
	
	}
	private static void testSingle() {
		String question ="What is the city of Germany ?";
			qb.setQuery(question);
			qb.buildQuery();
			String nqs = qb.getCharacterizedString();
			Nqs q1 = new Nqs(question,nqs,"","");
			//Interaction : Check query type
        	QueryAnnotaion.annotate(q1);
        	System.out.println(q1.predicateCandidate);
        	//Interaction : Check Predicate and Entity
        	try {
				System.out.print(TempalateGeneratorServer.generator(q1.predicateCandidate,q1.resourceSpotlight));
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
	
	private static void testQALD() {
		for(int i=15;i<121;i++)
		{	System.out.print((i+1)+"\t");
		evaluate(i);
		}	
	}
	static void evaluate(int n){
		List<Nqs> templates = Parser.parse();
		Nqs q1 = templates.get(n);
		System.out.print(q1.nlQuery +"\t");
		QueryAnnotaion.annotate(q1);
		System.out.print(q1.predicateCandidate);
		System.out.println();
	}
}
