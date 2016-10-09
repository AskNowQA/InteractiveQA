package tech.sda.iqa.benchmark;

import java.util.List;

import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.interactiveqa.Parser;
import tech.sda.iqa.util.annotation.QueryAnnotaion;

public class BenchmarkEvalution {

	public static void main(String[] args)
	{
		for(int i=1;i<349;i++)
		{	System.out.print((i+1)+"\t");
		evaluate(i);

		}
	}
	static void evaluate(int n)
	{
		List<Nqs> templates = Parser.parse();
		Nqs q1 = templates.get(n);
		System.out.print(q1.nlQuery +"\t");
		QueryAnnotaion.annotate(q1);
		System.out.print(q1.predicateCandidate);
		System.out.println();
		
	}
}
