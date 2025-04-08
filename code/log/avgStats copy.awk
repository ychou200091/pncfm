BEGIN {
	printf("Bandwidth      Lost      Total Datagrams\n");
	num_count=0;
	count=0;
	sum=0;
}
{

    if($5 == "sec") {       
		if($8 != "received") {            
			printf("%-9s", $8);
			printf("      ");
			printf("%-9s", substr($12, 1, length($12)-1));
			printf("      ");
			printf("%-9s\n", $13);
			sum+=$8;
			count+=1;
		}
    }else if($4 == "sec") {
		if($7 != "received") {            
			printf("%-9s", $7);
			printf("      ");
			printf("%-9s", substr($11, 1, length($11)-1));
			printf("      ");
			printf("%-9s\n", $12);
			sum+=$7;
			count+=1;
		}
	}
	
	if (count==3){
	#printf("%-9f \n",sum/3.);
	vector[num_count]=sum/3;
	num_count++;
	count=0;
	sum=0;
	}

                
}
END{    
	for(i=0;i<num_count;i++){
		printf("%-9f \t",vector[i]);
	}
	
}
