import qcportal as ptl


def test_qcportal():
    client = ptl.PortalClient("https://qcademo.molssi.org", verify=False)
    print(client)
    first_record = client.get_records(1)
    print(first_record)
    assert -1.1117197122934774 == first_record.properties["scf_total_energy"]
    datasets = client.list_datasets()
    for dataset in datasets:
        print(
            f"Name: {dataset['dataset_name']}, Type: {dataset['dataset_type']}")
    ds = client.get_dataset(
        dataset_type="singlepoint", dataset_name="Element Benchmark"
    )
    print(ds.description)
    df = ds.get_properties_df(["scf_total_energy", "scf_iterations"])
    print(df)
    assert (
        df[df.index == "ne_atom"][("hf/sto-3g", "scf_total_energy")].iloc[0]
        == -126.60457333960916
    )
    return


def main():
    test_qcportal()
    return


if __name__ == "__main__":
    main()
