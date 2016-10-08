package tech.sda.iqa.util.annotation;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import tech.sda.iqa.interactiveqa.Nqs;

public class PredicateAnnotation {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

	public static Set<String> getPredicateAnnotation(Nqs n) {
		// TODO Auto-generated method stub
	 Set<String> Predicate = new HashSet<String>();
		//extract predicate candidate from NQS
		//String sc;
	 String temp;
		try{
			temp =n.getDesire();
				//count(xyz) --> xyz
			if(temp.contains("(")&&temp.contains(")"))
				temp = temp.substring(temp.indexOf("(")+1, temp.indexOf(")"));
			
			Predicate.add(temp);
			Predicate.add(n.getRelation2());
			Predicate=clearNoise (Predicate);

		}
		catch(Exception e){
			//Predicate = null;
			
		}

		return Predicate;
	}
	private static Set<String> clearNoise(Set<String> predicate) {
		// TODO Auto-generated method stub
		String[] stopwords = { "of","list",
				"have","had","has","more","through","than","the",
				"does","did","do","as","is","are","was","were","a","an",
				"by","from","to","for","need","I","you","in","on"};
		Set<String> temp = new HashSet<String>();
		for(String p : predicate){
			String[] words = p.split("\\s+");
			//System.out.print(p+"-");
				for(int i=0;i<words.length;i++){
					
					for(String s: stopwords){
						//System.out.print(s + "="+words[i]+";");
						if(s.equalsIgnoreCase(words[i])){
							words[i]="";
							//System.out.println("HIT");break;
						}
					}
					if(!words[i].equalsIgnoreCase(""))
					temp.add(words[i]);
					}
					//String word = words.toString();
					//System.out.print("777"+words.toString());//cleaning
					//temp.add(word);
					//correct word
					//if not null: add to candidate list
				
		}
		//System.out.println(temp);
		return temp;
	}


}
